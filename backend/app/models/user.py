from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    google_id = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), default="", nullable=False)
    avatar_url = Column(String(512), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)
    is_removed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    notes_created = relationship("Note", back_populates="creator", foreign_keys="Note.created_by")
    audit_logs = relationship("AuditLog", back_populates="user")
