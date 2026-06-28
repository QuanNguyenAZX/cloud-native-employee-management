import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute, redirect } from "@tanstack/react-router"
import { Suspense } from "react"

import {
  DepartmentsService,
  EmployeesService,
  UsersService,
  type DepartmentPublic,
} from "@/client"
import AddEmployee from "@/components/Employees/AddEmployee"
import { columns, type EmployeeTableData } from "@/components/Employees/columns"
import PendingEmployees from "@/components/Employees/PendingEmployees"
import { DataTable } from "@/components/Common/DataTable"

function getEmployeesQueryOptions() {
  return {
    queryFn: () => EmployeesService.readEmployees({ page: 1, size: 100 }),
    queryKey: ["employees"],
  }
}

function getDepartmentsQueryOptions() {
  return {
    queryFn: () => DepartmentsService.readDepartments({ page: 1, size: 100 }),
    queryKey: ["departments"],
  }
}

export const Route = createFileRoute("/_layout/employees")({
  component: Employees,
  beforeLoad: async () => {
    const user = await UsersService.readUserMe()
    if (!(user.is_superuser || user.role === "admin")) {
      throw redirect({ to: "/" })
    }
  },
  head: () => ({
    meta: [{ title: "Employees - FastAPI Template" }],
  }),
})

function EmployeesTableContent() {
  const { data: employees } = useSuspenseQuery(getEmployeesQueryOptions())
  const { data: departments } = useSuspenseQuery(getDepartmentsQueryOptions())

  const departmentMap = new Map(
    departments.data.map((department: DepartmentPublic) => [
      department.id,
      department.name,
    ]),
  )

  const tableData: EmployeeTableData[] = employees.data.map((employee) => ({
    ...employee,
    department_name: departmentMap.get(employee.department_id) ?? "",
  }))

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Employees</h1>
          <p className="text-muted-foreground">
            Manage employee records and department assignments.
          </p>
        </div>
        <AddEmployee departments={departments.data} />
      </div>
      <DataTable columns={columns(departments.data)} data={tableData} />
    </div>
  )
}

function Employees() {
  return (
    <Suspense fallback={<PendingEmployees />}>
      <EmployeesTableContent />
    </Suspense>
  )
}
