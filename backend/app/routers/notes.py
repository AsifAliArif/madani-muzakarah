from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth.security import get_admin_user, get_current_user
from app.database import get_db
from app.models.note import Note, NoteStatus
from app.models.user import User
from app.schemas import NoteCreate, NoteOut, NoteUpdate, SearchRequest, SearchResult
from app.services.ai_formatting import apply_ai_formatting_to_html
from app.services.llm import call_llm
from app.services.notes import (
    fetch_note,
    html_to_plain,
    log_audit,
    note_state_dict,
    note_to_out,
    sync_note_categories,
)
from app.services.search import index_note, remove_note, search_notes
from app.models.ai_settings import AISettings
from app.websocket.manager import manager

router = APIRouter(prefix="/api/notes", tags=["notes"])


async def process_ai_formatting(note_id: UUID, db_url: str):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        note = fetch_note(db, note_id)
        if not note:
            return
        settings = db.query(AISettings).first()
        if not settings or not settings.api_key_encrypted:
            return
        plain = note.content_plain or html_to_plain(note.content_html)
        extracted = await call_llm(settings, plain)
        if not extracted:
            return
        new_html = apply_ai_formatting_to_html(note.content_html, extracted)
        if new_html != note.content_html:
            note.content_html = new_html
            note.content_plain = html_to_plain(new_html)
            db.commit()
            out = note_to_out(note)
            index_note(out)
            await manager.broadcast("note_updated", out.model_dump())
    finally:
        db.close()


@router.get("", response_model=list[NoteOut])
def list_notes(
    status: str = Query("active"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        note_status = NoteStatus(status)
    except ValueError:
        raise HTTPException(400, "غلط اسٹیٹس")
    if note_status == NoteStatus.trashed and user.role.value != "admin":
        raise HTTPException(403, "ٹریش صرف ایڈمن دیکھ سکتا ہے")

    from sqlalchemy.orm import joinedload
    from app.models.note import NoteCategory

    notes = (
        db.query(Note)
        .options(joinedload(Note.note_categories).joinedload(NoteCategory.category), joinedload(Note.creator))
        .filter(Note.status == note_status)
        .order_by(Note.updated_at.desc())
        .all()
    )
    return [note_to_out(n) for n in notes]


@router.get("/{note_id}", response_model=NoteOut)
def get_note(note_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    note = fetch_note(db, note_id)
    if not note:
        raise HTTPException(404, "نوٹ نہیں ملا")
    if note.status == NoteStatus.trashed and user.role.value != "admin":
        raise HTTPException(404, "نوٹ نہیں ملا")
    return note_to_out(note)


@router.post("", response_model=NoteOut)
async def create_note(
    payload: NoteCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from app.config import settings
    plain = html_to_plain(payload.content_html)
    note = Note(
        title=payload.title.strip() if payload.title else None,
        content_html=payload.content_html,
        content_plain=plain,
        author_name=payload.author_name.strip(),
        status=NoteStatus.active,
        created_by=user.id,
        updated_by=user.id,
    )
    db.add(note)
    db.flush()
    sync_note_categories(db, note, payload.category_names)
    log_audit(db, note.id, user.id, "create", None, note_state_dict(note))
    db.commit()
    note = fetch_note(db, note.id)
    out = note_to_out(note)
    index_note(out)
    await manager.broadcast("note_created", out.model_dump())
    background_tasks.add_task(process_ai_formatting, note.id, settings.database_url)
    return out


@router.put("/{note_id}", response_model=NoteOut)
async def update_note(
    note_id: UUID,
    payload: NoteUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from app.config import settings
    note = fetch_note(db, note_id)
    if not note:
        raise HTTPException(404, "نوٹ نہیں ملا")
    if note.status == NoteStatus.trashed:
        raise HTTPException(400, "ٹریش میں نوٹ ترمیم نہیں ہو سکتا")

    prev = note_state_dict(note)
    note.title = payload.title.strip() if payload.title else None
    note.content_html = payload.content_html
    note.content_plain = html_to_plain(payload.content_html)
    note.author_name = payload.author_name.strip()
    note.updated_by = user.id
    sync_note_categories(db, note, payload.category_names)
    log_audit(db, note.id, user.id, "update", prev, note_state_dict(note))
    db.commit()
    note = fetch_note(db, note.id)
    out = note_to_out(note)
    index_note(out)
    await manager.broadcast("note_updated", out.model_dump())
    background_tasks.add_task(process_ai_formatting, note.id, settings.database_url)
    return out


@router.post("/{note_id}/archive", response_model=NoteOut)
async def archive_note(note_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    note = fetch_note(db, note_id)
    if not note:
        raise HTTPException(404, "نوٹ نہیں ملا")
    prev = note_state_dict(note)
    note.status = NoteStatus.archived
    note.updated_by = user.id
    log_audit(db, note.id, user.id, "archive", prev, note_state_dict(note))
    db.commit()
    note = fetch_note(db, note.id)
    out = note_to_out(note)
    remove_note(str(note.id))
    await manager.broadcast("note_archived", {"id": str(note.id)})
    return out


@router.post("/{note_id}/trash", response_model=NoteOut)
async def trash_note(note_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    note = fetch_note(db, note_id)
    if not note:
        raise HTTPException(404, "نوٹ نہیں ملا")
    prev = note_state_dict(note)
    note.status = NoteStatus.trashed
    note.updated_by = user.id
    log_audit(db, note.id, user.id, "trash", prev, note_state_dict(note))
    db.commit()
    note = fetch_note(db, note.id)
    out = note_to_out(note)
    remove_note(str(note.id))
    await manager.broadcast("note_trashed", {"id": str(note.id)})
    return out


@router.post("/{note_id}/restore", response_model=NoteOut)
async def restore_note(
    note_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    note = fetch_note(db, note_id)
    if not note:
        raise HTTPException(404, "نوٹ نہیں ملا")
    prev = note_state_dict(note)
    note.status = NoteStatus.active
    note.updated_by = admin.id
    log_audit(db, note.id, admin.id, "restore", prev, note_state_dict(note))
    db.commit()
    note = fetch_note(db, note.id)
    out = note_to_out(note)
    index_note(out)
    await manager.broadcast("note_restored", out.model_dump())
    return out


@router.delete("/{note_id}/forever")
async def delete_forever(
    note_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    note = fetch_note(db, note_id)
    if not note or note.status != NoteStatus.trashed:
        raise HTTPException(404, "ٹریش میں نوٹ نہیں ملا")
    log_audit(db, note.id, admin.id, "delete_forever", note_state_dict(note), None)
    db.delete(note)
    db.commit()
    remove_note(str(note_id))
    await manager.broadcast("note_deleted", {"id": str(note_id)})
    return {"ok": True}


@router.post("/search", response_model=SearchResult)
def search(
    payload: SearchRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ids, total = search_notes(payload.query, payload.mode, payload.terms)
    if not ids:
        # Fallback to DB ilike search
        q = db.query(Note).filter(Note.status == NoteStatus.active)
        if payload.query:
            pattern = f"%{payload.query}%"
            q = q.filter(
                (Note.title.ilike(pattern)) | (Note.content_plain.ilike(pattern)) | (Note.author_name.ilike(pattern))
            )
        notes = q.order_by(Note.updated_at.desc()).limit(50).all()
        return SearchResult(notes=[note_to_out(n) for n in notes], total=len(notes))

    from uuid import UUID as UUIDType
    uuid_ids = [UUIDType(i) for i in ids]
    notes_map = {str(n.id): n for n in db.query(Note).filter(Note.id.in_(uuid_ids)).all()}
    ordered = [note_to_out(notes_map[i]) for i in ids if i in notes_map]
    return SearchResult(notes=ordered, total=total)
