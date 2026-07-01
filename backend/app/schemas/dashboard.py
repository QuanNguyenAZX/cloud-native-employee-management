from sqlmodel import SQLModel


class DashboardSummary(SQLModel):
    total_employees: int
    total_departments: int
    total_managers: int
    average_salary: float | None = None


class DashboardDepartmentStat(SQLModel):
    department_name: str
    count: int


class DashboardGrowthStat(SQLModel):
    period: str
    count: int


class DashboardSalaryBandStat(SQLModel):
    label: str
    count: int


class DashboardPublic(SQLModel):
    summary: DashboardSummary
    employee_by_department: list[DashboardDepartmentStat]
    employee_growth: list[DashboardGrowthStat]
    salary_distribution: list[DashboardSalaryBandStat]
