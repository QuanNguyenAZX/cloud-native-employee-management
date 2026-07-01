import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String
from sqlmodel import Field, Relationship, SQLModel

from app.core.storage import build_object_url
from app.models.utils import get_datetime_utc
from app.schemas.user import UserRole

if TYPE_CHECKING:
    from app.models.item import Item


class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    role: UserRole = Field(default=UserRole.employee, sa_type=String(length=20))
    full_name: str | None = Field(default=None, max_length=255)
    avatar_key: str | None = Field(default=None, max_length=255)
    hashed_password: str
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)

    @property
    def avatar_url(self) -> str | None:
        if not self.avatar_key:
            return None
        return build_object_url(self.avatar_key)
