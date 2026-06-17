from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class UserOut(BaseModel):
    id: UUID
    email: str
    name: str
    avatar_url: str | None
    role: str

    class Config:
        from_attributes = True


class CategoryOut(BaseModel):
    id: UUID
    name: str

    class Config:
        from_attributes = True


class NoteBase(BaseModel):
    title: str | None = None
    content_html: str = ""
    author_name: str = ""
    category_names: list[str] = Field(default_factory=list)


class NoteCreate(NoteBase):
    pass


class NoteUpdate(NoteBase):
    pass


class NoteOut(BaseModel):
    id: UUID
    title: str | None
    content_html: str
    content_plain: str
    author_name: str
    status: str
    categories: list[CategoryOut]
    created_by: UUID
    updated_by: UUID | None
    creator_name: str = ""
    created_at: datetime
    updated_at: datetime
    display_title: str = ""

    class Config:
        from_attributes = True


class AuditLogOut(BaseModel):
    id: UUID
    note_id: UUID | None
    user_id: UUID
    user_name: str = ""
    action: str
    previous_state: dict | None
    new_state: dict | None
    created_at: datetime

    class Config:
        from_attributes = True


class AISettingsOut(BaseModel):
    llm_name: str
    system_prompt: str
    has_api_key: bool


class AISettingsUpdate(BaseModel):
    llm_name: str
    api_key: str | None = None
    system_prompt: str


class SearchRequest(BaseModel):
    query: str = ""
    mode: str = "broad"  # word, phrase, exact, broad
    fields: list[str] = Field(default_factory=list)
    terms: list[str] = Field(default_factory=list)


class SearchResult(BaseModel):
    notes: list[NoteOut]
    total: int
