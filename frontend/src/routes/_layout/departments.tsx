import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute, redirect } from "@tanstack/react-router"
import { Suspense } from "react"

import { DepartmentsService, UsersService } from "@/client"
import { DataTable } from "@/components/Common/DataTable"
import AddDepartment from "@/components/Departments/AddDepartment"
import { columns } from "@/components/Departments/columns"
import PendingDepartments from "@/components/Departments/PendingDepartments"

function getDepartmentsQueryOptions() {
  return {
    queryFn: () => DepartmentsService.readDepartments({ page: 1, size: 100 }),
    queryKey: ["departments"],
  }
}

export const Route = createFileRoute("/_layout/departments")({
  component: Departments,
  beforeLoad: async () => {
    const user = await UsersService.readUserMe()
    if (
      !(user.is_superuser || user.role === "admin" || user.role === "manager")
    ) {
      throw redirect({ to: "/" })
    }
  },
  head: () => ({
    meta: [{ title: "Departments - FastAPI Template" }],
  }),
})

function DepartmentsTableContent() {
  const { data: departments } = useSuspenseQuery(getDepartmentsQueryOptions())

  return <DataTable columns={columns} data={departments.data} />
}

function DepartmentsTable() {
  return (
    <Suspense fallback={<PendingDepartments />}>
      <DepartmentsTableContent />
    </Suspense>
  )
}

function Departments() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Departments</h1>
          <p className="text-muted-foreground">
            Organize the company structure and keep it tidy.
          </p>
        </div>
        <AddDepartment />
      </div>
      <DepartmentsTable />
    </div>
  )
}
