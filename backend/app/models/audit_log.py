from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id", ondelete="SET NULL"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False)
    previous_state = Column(JSONB, nullable=True)
    new_state = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    note = relationship("Note", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs")
