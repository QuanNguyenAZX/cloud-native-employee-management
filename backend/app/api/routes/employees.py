import math
import uuid
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import asc, desc, or_
from sqlmodel import func, select

from app import crud
from app.api.deps import CurrentUser, SessionDep, get_current_manager_or_admin
from app.models import (
    Department,
    Employee,
    EmployeeCreate,
    EmployeePublic,
    EmployeesPublic,
    EmployeeUpdate,
    Message,
)

router = APIRouter(
    prefix="/employees",
    tags=["employees"],
    dependencies=[Depends(get_current_manager_or_admin)],
)


def _apply_employee_filters(
    statement,
    *,
    search: str | None,
    department_id: uuid.UUID | None,
    role: str | None,
    status: bool | None,
):
    if search:
        pattern = f"%{search.strip()}%"
        statement = statement.where(
            or_(
                Employee.full_name.ilike(pattern),
                Employee.email.ilike(pattern),
                Employee.job_title.ilike(pattern),
                Employee.phone.ilike(pattern),
                Department.name.ilike(pattern),
            )
        )
    if department_id:
        statement = statement.where(Employee.department_id == department_id)
    if role:
        statement = statement.where(Employee.job_title.ilike(f"%{role.strip()}%"))
    if status is not None:
        statement = statement.where(Employee.is_active == status)
    return statement


@router.get("/", response_model=EmployeesPublic)
def read_employees(
    session: SessionDep,
    page: int = 1,
    size: int = 10,
    search: str | None = None,
    department_id: uuid.UUID | None = None,
    role: str | None = None,
    status: bool | None = None,
    sort_by: Literal[
        "full_name", "email", "job_title", "salary", "created_at"
    ] = "created_at",
    sort_order: Literal["asc", "desc"] = "desc",
) -> Any:
    page = max(page, 1)
    size = min(max(size, 1), 100)
    sort_map = {
        "full_name": Employee.full_name,
        "email": Employee.email,
        "job_title": Employee.job_title,
        "salary": Employee.salary,
        "created_at": Employee.created_at,
    }
    sort_column = sort_map[sort_by]
    sort_fn = asc if sort_order == "asc" else desc

    base_statement = select(Employee).join(Department)
    base_statement = _apply_employee_filters(
        base_statement,
        search=search,
        department_id=department_id,
        role=role,
        status=status,
    )

    count_statement = select(func.count()).select_from(Employee).join(Department)
    count_statement = _apply_employee_filters(
        count_statement,
        search=search,
        department_id=department_id,
        role=role,
        status=status,
    )
    count = session.exec(count_statement).one()

    statement = (
        base_statement.order_by(sort_fn(sort_column))
        .offset((page - 1) * size)
        .limit(size)
    )
    employees = session.exec(statement).all()
    employees_public = [EmployeePublic.model_validate(item) for item in employees]
    pages = math.ceil(count / size) if count else 1
    return EmployeesPublic(
        data=employees_public, count=count, page=page, size=size, pages=pages
    )


@router.post("/", response_model=EmployeePublic)
def create_employee(
    *, session: SessionDep, employee_in: EmployeeCreate, current_user: CurrentUser
) -> Any:
    if crud.get_employee_by_email(session=session, email=employee_in.email):
        raise HTTPException(status_code=400, detail="Employee already exists")
    department = session.get(Department, employee_in.department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    employee = crud.create_employee(session=session, employee_in=employee_in)
    crud.create_audit_log(
        session=session,
        current_user=current_user,
        action="created",
        entity_type="Employee",
        entity_id=str(employee.id),
    )
    return employee


@router.get("/{employee_id}", response_model=EmployeePublic)
def read_employee(employee_id: uuid.UUID, session: SessionDep) -> Any:
    employee = session.get(Employee, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.put("/{employee_id}", response_model=EmployeePublic)
def update_employee(
    *,
    session: SessionDep,
    employee_id: uuid.UUID,
    employee_in: EmployeeUpdate,
    current_user: CurrentUser,
) -> Any:
    employee = session.get(Employee, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    if employee_in.email:
        existing_employee = crud.get_employee_by_email(
            session=session, email=employee_in.email
        )
        if existing_employee and existing_employee.id != employee_id:
            raise HTTPException(status_code=409, detail="Employee already exists")
    if employee_in.department_id:
        department = session.get(Department, employee_in.department_id)
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")
    before_data = employee.model_dump()
    updated_employee = crud.update_employee(
        session=session, db_employee=employee, employee_in=employee_in
    )
    crud.create_audit_log(
        session=session,
        current_user=current_user,
        action="updated",
        entity_type="Employee",
        entity_id=str(updated_employee.id),
        before_data=before_data,
        after_data=updated_employee.model_dump(),
    )
    return updated_employee


@router.delete("/{employee_id}", response_model=Message)
def delete_employee(
    session: SessionDep, employee_id: uuid.UUID, current_user: CurrentUser
) -> Message:
    employee = session.get(Employee, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    before_data = employee.model_dump()
    session.delete(employee)
    session.commit()
    crud.create_audit_log(
        session=session,
        current_user=current_user,
        action="deleted",
        entity_type="Employee",
        entity_id=str(employee_id),
        before_data=before_data,
    )
    return Message(message="Employee deleted successfully")
