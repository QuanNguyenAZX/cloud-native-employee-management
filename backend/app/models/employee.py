import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship

from app.models.user import get_datetime_utc
from app.schemas.employee import EmployeeBase

if TYPE_CHECKING:
    from app.models.department import Department


class Employee(EmployeeBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    department_id: uuid.UUID = Field(
        foreign_key="department.id", nullable=False, ondelete="CASCADE"
    )
    department: Optional["Department"] = Relationship(back_populates="employees")
