"""initial

Revision ID: 001
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("google_id", sa.String(255), unique=True, nullable=False),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("avatar_url", sa.String(512), nullable=True),
        sa.Column("role", sa.Enum("admin", "user", name="userrole"), nullable=False),
        sa.Column("is_removed", sa.Boolean(), default=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), unique=True, nullable=False),
    )
    op.create_table(
        "notes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(500), nullable=True),
        sa.Column("content_html", sa.Text(), nullable=False),
        sa.Column("content_plain", sa.Text(), nullable=False),
        sa.Column("author_name", sa.String(255), nullable=False),
        sa.Column("status", sa.Enum("active", "archived", "trashed", name="notestatus"), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "note_categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("note_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("notes.id", ondelete="CASCADE")),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("categories.id", ondelete="CASCADE")),
        sa.UniqueConstraint("note_id", "category_id", name="uq_note_category"),
    )
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("note_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("notes.id", ondelete="SET NULL"), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("previous_state", postgresql.JSONB(), nullable=True),
        sa.Column("new_state", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "ai_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("llm_name", sa.String(100), nullable=False),
        sa.Column("api_key_encrypted", sa.String(512), nullable=False),
        sa.Column("system_prompt", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("ai_settings")
    op.drop_table("audit_logs")
    op.drop_table("note_categories")
    op.drop_table("notes")
    op.drop_table("categories")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS notestatus")
    op.execute("DROP TYPE IF EXISTS userrole")
