import uuid
from datetime import date, datetime

from pydantic import EmailStr, field_validator
from sqlmodel import Field, SQLModel


def validate_birth_date(value: date | None) -> date | None:
    if value and value > date.today():
        raise ValueError("Birth date cannot be in the future")
    return value


class EmployeeBase(SQLModel):
    full_name: str = Field(min_length=1, max_length=255)
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    job_title: str = Field(min_length=1, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    is_active: bool = True
    salary: float | None = Field(default=None, ge=0)
    birth_date: date | None = None

    @field_validator("birth_date")
    @classmethod
    def _validate_birth_date(cls, value: date | None) -> date | None:
        return validate_birth_date(value)


class EmployeeCreate(EmployeeBase):
    department_id: uuid.UUID


class EmployeeUpdate(SQLModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore[assignment]
    job_title: str | None = Field(default=None, min_length=1, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    is_active: bool | None = None
    salary: float | None = Field(default=None, ge=0)
    birth_date: date | None = None
    department_id: uuid.UUID | None = None

    @field_validator("birth_date")
    @classmethod
    def _validate_birth_date(cls, value: date | None) -> date | None:
        return validate_birth_date(value)


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
