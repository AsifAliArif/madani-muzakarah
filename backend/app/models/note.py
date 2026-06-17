from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class NoteStatus(str, enum.Enum):
    active = "active"
    archived = "archived"
    trashed = "trashed"


class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, index=True, nullable=False)

    notes = relationship("NoteCategory", back_populates="category")


class NoteCategory(Base):
    __tablename__ = "note_categories"
    __table_args__ = (UniqueConstraint("note_id", "category_id", name="uq_note_category"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)

    note = relationship("Note", back_populates="note_categories")
    category = relationship("Category", back_populates="notes")


class Note(Base):
    __tablename__ = "notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=True)
    content_html = Column(Text, default="", nullable=False)
    content_plain = Column(Text, default="", nullable=False)
    author_name = Column(String(255), default="", nullable=False)
    status = Column(Enum(NoteStatus), default=NoteStatus.active, index=True, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    creator = relationship("User", back_populates="notes_created", foreign_keys=[created_by])
    note_categories = relationship("NoteCategory", back_populates="note", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="note")
