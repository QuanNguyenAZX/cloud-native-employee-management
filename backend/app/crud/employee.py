from typing import Any

from sqlmodel import Session, select

from app.models import Employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate


def create_employee(*, session: Session, employee_in: EmployeeCreate) -> Employee:
    db_obj = Employee.model_validate(employee_in)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_employee(
    *, session: Session, db_employee: Employee, employee_in: EmployeeUpdate
) -> Any:
    employee_data = employee_in.model_dump(exclude_unset=True)
    db_employee.sqlmodel_update(employee_data)
    session.add(db_employee)
    session.commit()
    session.refresh(db_employee)
    return db_employee


def get_employee_by_email(*, session: Session, email: str) -> Employee | None:
    statement = select(Employee).where(Employee.email == email)
    return session.exec(statement).first()
