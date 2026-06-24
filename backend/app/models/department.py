import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship

from app.models.user import get_datetime_utc
from app.schemas.department import DepartmentBase

if TYPE_CHECKING:
    from app.models.employee import Employee


class Department(DepartmentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    employees: list["Employee"] = Relationship(
        back_populates="department", cascade_delete=True
    )
