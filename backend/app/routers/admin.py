from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.security import encrypt_value, get_admin_user
from app.database import get_db
from app.models.ai_settings import AISettings, DEFAULT_SYSTEM_PROMPT
from sqlalchemy.orm import joinedload

from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas import AISettingsOut, AISettingsUpdate, AuditLogOut, CategoryOut, UserOut
from app.models.note import Category

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [UserOut(id=u.id, email=u.email, name=u.name, avatar_url=u.avatar_url, role=u.role.value) for u in users]


@router.post("/users/{user_id}/remove")
def remove_user(user_id: UUID, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "صارف نہیں ملا")
    if user.email.lower() == admin.email.lower():
        raise HTTPException(400, "ایڈمن خود کو نہیں ہٹا سکتا")
    user.is_removed = True
    db.commit()
    return {"ok": True}


@router.get("/logs", response_model=list[AuditLogOut])
def list_logs(db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    logs = (
        db.query(AuditLog)
        .options(joinedload(AuditLog.user))
        .order_by(AuditLog.created_at.desc())
        .limit(200)
        .all()
    )
    result = []
    for log in logs:
        user_name = log.user.name if log.user else ""
        result.append(AuditLogOut(
            id=log.id,
            note_id=log.note_id,
            user_id=log.user_id,
            user_name=user_name,
            action=log.action,
            previous_state=log.previous_state,
            new_state=log.new_state,
            created_at=log.created_at,
        ))
    return result


@router.get("/ai-settings", response_model=AISettingsOut)
def get_ai_settings(db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    settings = db.query(AISettings).first()
    if not settings:
        settings = AISettings()
        db.add(settings)
        db.commit()
    return AISettingsOut(
        llm_name=settings.llm_name,
        system_prompt=settings.system_prompt,
        has_api_key=bool(settings.api_key_encrypted),
    )


@router.put("/ai-settings", response_model=AISettingsOut)
def update_ai_settings(
    payload: AISettingsUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    settings = db.query(AISettings).first()
    if not settings:
        settings = AISettings()
        db.add(settings)
    settings.llm_name = payload.llm_name
    settings.system_prompt = payload.system_prompt or DEFAULT_SYSTEM_PROMPT
    if payload.api_key:
        settings.api_key_encrypted = encrypt_value(payload.api_key)
    db.commit()
    return AISettingsOut(
        llm_name=settings.llm_name,
        system_prompt=settings.system_prompt,
        has_api_key=bool(settings.api_key_encrypted),
    )


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    cats = db.query(Category).order_by(Category.name).all()
    return [CategoryOut(id=c.id, name=c.name) for c in cats]
