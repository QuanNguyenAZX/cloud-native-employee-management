import uuid
from datetime import datetime

from sqlalchemy import DateTime, JSON
from sqlmodel import Field, SQLModel

from app.models.utils import get_datetime_utc


class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_log"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    actor_id: uuid.UUID | None = Field(
        default=None, foreign_key="user.id", nullable=True, index=True
    )
    actor_email: str | None = Field(default=None, max_length=255, index=True)
    actor_role: str | None = Field(default=None, max_length=20, index=True)
    action: str = Field(max_length=50, index=True)
    entity_type: str = Field(max_length=50, index=True)
    entity_id: str | None = Field(default=None, max_length=64, index=True)
    detail: str = Field(max_length=255)
    before_data: dict | None = Field(default=None, sa_type=JSON)
    after_data: dict | None = Field(default=None, sa_type=JSON)
    created_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
