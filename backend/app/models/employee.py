import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.models.utils import get_datetime_utc

if TYPE_CHECKING:
    from app.models.department import Department


class Employee(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    full_name: str = Field(min_length=1, max_length=255)
    email: str = Field(unique=True, index=True, max_length=255)
    job_title: str = Field(min_length=1, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    is_active: bool = True
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    department_id: uuid.UUID = Field(
        foreign_key="department.id", nullable=False, ondelete="CASCADE"
    )
    department: Optional["Department"] = Relationship(back_populates="employees")
