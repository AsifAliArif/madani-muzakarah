import re
import html as html_lib
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from app.models.audit_log import AuditLog
from app.models.note import Category, Note, NoteCategory, NoteStatus
from app.schemas import CategoryOut, NoteOut


def html_to_plain(html: str) -> str:
    text = re.sub(r"<br\s*/?>", "\n", html, flags=re.I)
    text = re.sub(r"</p>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    return html_lib.unescape(text).strip()


def get_display_title(note: Note) -> str:
    if note.title and note.title.strip():
        return note.title.strip()
    plain = note.content_plain or html_to_plain(note.content_html)
    first_line = plain.split("\n")[0].strip() if plain else "بلا عنوان"
    return first_line or "بلا عنوان"


def note_to_out(note: Note) -> NoteOut:
    categories = [
        CategoryOut(id=nc.category.id, name=nc.category.name)
        for nc in note.note_categories
        if nc.category
    ]
    creator_name = note.creator.name if note.creator else ""
    return NoteOut(
        id=note.id,
        title=note.title,
        content_html=note.content_html,
        content_plain=note.content_plain,
        author_name=note.author_name,
        status=note.status.value,
        categories=categories,
        created_by=note.created_by,
        updated_by=note.updated_by,
        creator_name=creator_name,
        created_at=note.created_at,
        updated_at=note.updated_at,
        display_title=get_display_title(note),
    )


def get_or_create_categories(db: Session, names: list[str]) -> list[Category]:
    categories = []
    for name in names:
        name = name.strip()
        if not name:
            continue
        cat = db.query(Category).filter(Category.name == name).first()
        if not cat:
            cat = Category(name=name)
            db.add(cat)
            db.flush()
        categories.append(cat)
    return categories


def sync_note_categories(db: Session, note: Note, names: list[str]):
    note.note_categories.clear()
    db.flush()
    for cat in get_or_create_categories(db, names):
        note.note_categories.append(NoteCategory(note_id=note.id, category_id=cat.id))


def log_audit(db: Session, note_id: Optional[UUID], user_id: UUID, action: str, prev: Optional[dict], new: Optional[dict]):
    db.add(AuditLog(
        note_id=note_id,
        user_id=user_id,
        action=action,
        previous_state=prev,
        new_state=new,
    ))


def note_state_dict(note: Note) -> dict:
    return {
        "title": note.title,
        "content_html": note.content_html,
        "author_name": note.author_name,
        "status": note.status.value,
        "categories": [nc.category.name for nc in note.note_categories if nc.category],
    }


def fetch_note(db: Session, note_id: UUID) -> Optional[Note]:
    return (
        db.query(Note)
        .options(joinedload(Note.note_categories).joinedload(NoteCategory.category), joinedload(Note.creator))
        .filter(Note.id == note_id)
        .first()
    )
