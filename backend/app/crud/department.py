from typing import Any

from sqlmodel import Session, select

from app.models import Department
from app.schemas.department import DepartmentCreate, DepartmentUpdate


def create_department(
    *, session: Session, department_in: DepartmentCreate
) -> Department:
    db_obj = Department.model_validate(department_in)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_department(
    *, session: Session, db_department: Department, department_in: DepartmentUpdate
) -> Any:
    department_data = department_in.model_dump(exclude_unset=True)
    db_department.sqlmodel_update(department_data)
    session.add(db_department)
    session.commit()
    session.refresh(db_department)
    return db_department


def get_department_by_name(*, session: Session, name: str) -> Department | None:
    statement = select(Department).where(Department.name == name)
    return session.exec(statement).first()
