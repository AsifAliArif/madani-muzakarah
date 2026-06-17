import base64
import hashlib
from datetime import datetime, timedelta

from cryptography.fernet import Fernet
from fastapi import Depends, HTTPException, Request
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User, UserRole

ALGORITHM = "HS256"
COOKIE_NAME = "muzakarah_token"


def _get_fernet() -> Fernet:
    key = settings.encryption_key
    if not key:
        derived = hashlib.sha256(settings.secret_key.encode()).digest()
        key = base64.urlsafe_b64encode(derived)
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt_value(value: str) -> str:
    if not value:
        return ""
    return _get_fernet().encrypt(value.encode()).decode()


def decrypt_value(value: str) -> str:
    if not value:
        return ""
    return _get_fernet().decrypt(value.encode()).decode()


def create_access_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode({"sub": user_id, "exp": expire}, settings.secret_key, algorithm=ALGORITHM)


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
    if not token:
        raise HTTPException(status_code=401, detail="لاگ ان ضروری ہے")
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="سیشن ختم ہو گیا")
    user = db.query(User).filter(User.id == user_id, User.is_removed == False).first()
    if not user:
        raise HTTPException(status_code=401, detail="صارف نہیں ملا")
    return user


def get_admin_user(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="ایڈمن کی اجازت ضروری ہے")
    return user
