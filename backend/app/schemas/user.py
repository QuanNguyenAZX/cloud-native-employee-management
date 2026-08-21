import uuid
from datetime import datetime
from enum import Enum
from typing import Annotated

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class UserRole(str, Enum):
    admin = "admin"
    manager = "manager"
    employee = "employee"


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    role: UserRole = Field(default=UserRole.employee)
    full_name: str | None = Field(default=None, max_length=255)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


class UserUpdate(SQLModel):
    email: Annotated[EmailStr | None, Field(max_length=255)] = None
    password: Annotated[str | None, Field(min_length=8, max_length=128)] = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    role: UserRole | None = None
    full_name: Annotated[str | None, Field(max_length=255)] = None


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime | None = None
    avatar_url: str | None = None


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int
