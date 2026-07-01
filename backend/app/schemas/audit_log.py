import uuid
from datetime import datetime
from typing import Any

from sqlmodel import SQLModel


class AuditLogBase(SQLModel):
    actor_id: uuid.UUID | None = None
    actor_email: str | None = None
    actor_role: str | None = None
    action: str
    entity_type: str
    entity_id: str | None = None
    detail: str
    before_data: dict[str, Any] | None = None
    after_data: dict[str, Any] | None = None
    created_at: datetime | None = None


class AuditLogPublic(AuditLogBase):
    id: uuid.UUID


class AuditLogsPublic(SQLModel):
    data: list[AuditLogPublic]
    count: int
    page: int = 1
    size: int = 10
    pages: int = 1
