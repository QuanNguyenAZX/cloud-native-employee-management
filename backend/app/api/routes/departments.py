import math
import uuid
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import asc, desc, or_
from sqlmodel import col, func, select

from app import crud
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
    get_current_manager_or_admin,
)
from app.models import (
    Department,
    DepartmentCreate,
    DepartmentPublic,
    DepartmentsPublic,
    DepartmentUpdate,
    Employee,
    Message,
)

router = APIRouter(prefix="/departments", tags=["departments"])


def _apply_department_filters(
    statement,
    *,
    search: str | None,
    is_active: bool | None,
):
    if search:
        pattern = f"%{search.strip()}%"
        statement = statement.where(
            or_(
                Department.name.ilike(pattern),
                Department.description.ilike(pattern),
            )
        )
    if is_active is not None:
        statement = statement.where(Department.is_active == is_active)
    return statement


@router.get(
    "/",
    response_model=DepartmentsPublic,
    dependencies=[Depends(get_current_manager_or_admin)],
)
def read_departments(
    session: SessionDep,
    page: int = 1,
    size: int = 10,
    search: str | None = None,
    is_active: bool | None = None,
    sort_by: Literal["name", "created_at"] = "created_at",
    sort_order: Literal["asc", "desc"] = "desc",
) -> Any:
    page = max(page, 1)
    size = min(max(size, 1), 100)
    sort_map = {
        "name": Department.name,
        "created_at": Department.created_at,
    }
    sort_column = sort_map[sort_by]
    sort_fn = asc if sort_order == "asc" else desc

    base_statement = select(Department)
    base_statement = _apply_department_filters(
        base_statement, search=search, is_active=is_active
    )

    count_statement = select(func.count()).select_from(Department)
    count_statement = _apply_department_filters(
        count_statement, search=search, is_active=is_active
    )
    count = session.exec(count_statement).one()

    statement = (
        base_statement.order_by(sort_fn(sort_column))
        .offset((page - 1) * size)
        .limit(size)
    )
    departments = session.exec(statement).all()
    departments_public = [DepartmentPublic.model_validate(item) for item in departments]
    pages = math.ceil(count / size) if count else 1
    return DepartmentsPublic(
        data=departments_public,
        count=count,
        page=page,
        size=size,
        pages=pages,
    )


@router.post(
    "/",
    response_model=DepartmentPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
def create_department(
    *, session: SessionDep, department_in: DepartmentCreate, current_user: CurrentUser
) -> Any:
    if crud.get_department_by_name(session=session, name=department_in.name):
        raise HTTPException(status_code=400, detail="Department already exists")
    department = crud.create_department(session=session, department_in=department_in)
    crud.create_audit_log(
        session=session,
        current_user=current_user,
        action="created",
        entity_type="Department",
        entity_id=str(department.id),
    )
    return department


@router.get(
    "/{department_id}",
    response_model=DepartmentPublic,
    dependencies=[Depends(get_current_manager_or_admin)],
)
def read_department(department_id: uuid.UUID, session: SessionDep) -> Any:
    department = session.get(Department, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return department


@router.put(
    "/{department_id}",
    response_model=DepartmentPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
def update_department(
    *,
    session: SessionDep,
    department_id: uuid.UUID,
    department_in: DepartmentUpdate,
    current_user: CurrentUser,
) -> Any:
    department = session.get(Department, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    if department_in.name:
        existing_department = crud.get_department_by_name(
            session=session, name=department_in.name
        )
        if existing_department and existing_department.id != department_id:
            raise HTTPException(status_code=409, detail="Department already exists")
    before_data = department.model_dump()
    updated_department = crud.update_department(
        session=session, db_department=department, department_in=department_in
    )
    crud.create_audit_log(
        session=session,
        current_user=current_user,
        action="updated",
        entity_type="Department",
        entity_id=str(updated_department.id),
        before_data=before_data,
        after_data=updated_department.model_dump(),
    )
    return updated_department


@router.delete(
    "/{department_id}",
    response_model=Message,
    dependencies=[Depends(get_current_active_superuser)],
)
def delete_department(
    session: SessionDep, department_id: uuid.UUID, current_user: CurrentUser
) -> Message:
    department = session.get(Department, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    employee_count = session.exec(
        select(func.count()).select_from(Employee).where(Employee.department_id == department_id)
    ).one()
    if employee_count:
        raise HTTPException(
            status_code=400,
            detail="Department has employees. Reassign or delete them first.",
        )
    before_data = department.model_dump()
    session.delete(department)
    session.commit()
    crud.create_audit_log(
        session=session,
        current_user=current_user,
        action="deleted",
        entity_type="Department",
        entity_id=str(department_id),
        before_data=before_data,
    )
    return Message(message="Department deleted successfully")
