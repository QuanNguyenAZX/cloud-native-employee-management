import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class DepartmentBase(SQLModel):
    name: str = Field(min_length=1, max_length=255, unique=True, index=True)
    description: str | None = Field(default=None, max_length=255)
    is_active: bool = True


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None


class DepartmentPublic(DepartmentBase):
    id: uuid.UUID
    created_at: datetime | None = None


class DepartmentsPublic(SQLModel):
    data: list[DepartmentPublic]
    count: int
    page: int = 1
    size: int = 10
    pages: int = 1
