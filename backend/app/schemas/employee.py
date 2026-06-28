import uuid
from datetime import datetime

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class EmployeeBase(SQLModel):
    full_name: str = Field(min_length=1, max_length=255)
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    job_title: str = Field(min_length=1, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    is_active: bool = True


class EmployeeCreate(EmployeeBase):
    department_id: uuid.UUID


class EmployeeUpdate(SQLModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore[assignment]
    job_title: str | None = Field(default=None, min_length=1, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    is_active: bool | None = None
    department_id: uuid.UUID | None = None


class EmployeePublic(EmployeeBase):
    id: uuid.UUID
    department_id: uuid.UUID
    created_at: datetime | None = None


class EmployeesPublic(SQLModel):
    data: list[EmployeePublic]
    count: int
    page: int = 1
    size: int = 10
    pages: int = 1
