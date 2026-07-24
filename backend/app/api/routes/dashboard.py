from collections import defaultdict
from datetime import date
from typing import Any

from fastapi import APIRouter
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Department, Employee, User, UserRole
from app.schemas.dashboard import (
    DashboardDepartmentStat,
    DashboardGrowthStat,
    DashboardPublic,
    DashboardSalaryBandStat,
    DashboardSummary,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _month_key(value: date) -> str:
    return value.strftime("%Y-%m")


@router.get("/", response_model=DashboardPublic)
def read_dashboard(session: SessionDep, _current_user: CurrentUser) -> Any:
    total_employees = session.exec(select(func.count()).select_from(Employee)).one()
    total_departments = session.exec(select(func.count()).select_from(Department)).one()
    total_managers = session.exec(
        select(func.count()).select_from(User).where(User.role == UserRole.manager)
    ).one()
    average_salary = session.exec(
        select(func.avg(Employee.salary)).where(Employee.salary.is_not(None))
    ).one()

    department_rows = session.exec(
        select(Department.name, func.count(Employee.id))
        .select_from(Department)
        .outerjoin(Employee, Employee.department_id == Department.id)
        .group_by(Department.id, Department.name)
        .order_by(Department.name.asc())
    ).all()
    employee_by_department = [
        DashboardDepartmentStat(department_name=name, count=count or 0)
        for name, count in department_rows
    ]

    growth_counter: dict[str, int] = defaultdict(int)
    employees = session.exec(select(Employee.created_at, Employee.salary)).all()
    for created_at, _salary in employees:
        if not created_at:
            continue
        growth_counter[_month_key(created_at.date())] += 1

    growth_items = sorted(growth_counter.items())
    employee_growth = [
        DashboardGrowthStat(period=period, count=count)
        for period, count in growth_items
    ]

    salary_values = [
        salary for (_created_at, salary) in employees if salary is not None
    ]
    salary_bins = [
        ("0-5k", 0, 5000),
        ("5k-10k", 5000, 10000),
        ("10k-20k", 10000, 20000),
        ("20k+", 20000, None),
    ]
    salary_distribution: list[DashboardSalaryBandStat] = []
    for label, lower, upper in salary_bins:
        if upper is None:
            count = sum(1 for value in salary_values if value >= lower)
        else:
            count = sum(1 for value in salary_values if lower <= value < upper)
        salary_distribution.append(DashboardSalaryBandStat(label=label, count=count))

    return DashboardPublic(
        summary=DashboardSummary(
            total_employees=total_employees,
            total_departments=total_departments,
            total_managers=total_managers,
            average_salary=float(average_salary)
            if average_salary is not None
            else None,
        ),
        employee_by_department=employee_by_department,
        employee_growth=employee_growth,
        salary_distribution=salary_distribution,
    )
