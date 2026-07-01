import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute, redirect, useNavigate } from "@tanstack/react-router"
import { type PaginationState } from "@tanstack/react-table"
import { Search, X } from "lucide-react"
import { Suspense } from "react"
import { z } from "zod"

import {
  type DepartmentPublic,
  DepartmentsService,
  EmployeesService,
  UsersService,
} from "@/client"
import { DataTable } from "@/components/Common/DataTable"
import AddEmployee from "@/components/Employees/AddEmployee"
import { columns, type EmployeeTableData } from "@/components/Employees/columns"
import PendingEmployees from "@/components/Employees/PendingEmployees"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

const searchSchema = z.object({
  page: z.coerce.number().catch(1),
  size: z.coerce.number().catch(10),
  search: z.string().catch(""),
  departmentId: z.string().catch(""),
  role: z.string().catch(""),
  status: z.enum(["all", "active", "inactive"]).catch("all"),
  sortBy: z
    .enum(["full_name", "email", "job_title", "salary", "created_at"])
    .catch("created_at"),
  sortOrder: z.enum(["asc", "desc"]).catch("desc"),
})

function getEmployeesQueryOptions(search: z.infer<typeof searchSchema>) {
  const status =
    search.status === "active"
      ? true
      : search.status === "inactive"
        ? false
        : undefined

  return {
    queryFn: () =>
      EmployeesService.readEmployees({
        page: search.page,
        size: search.size,
        search: search.search || undefined,
        departmentId: search.departmentId || undefined,
        role: search.role || undefined,
        status,
        sortBy: search.sortBy,
        sortOrder: search.sortOrder,
      }),
    queryKey: ["employees", search],
  }
}

function getDepartmentsQueryOptions() {
  return {
    queryFn: () => DepartmentsService.readDepartments({ page: 1, size: 100 }),
    queryKey: ["departments"],
  }
}

export const Route = createFileRoute("/_layout/employees")({
  validateSearch: searchSchema,
  component: Employees,
  beforeLoad: async () => {
    const user = await UsersService.readUserMe()
    if (!(user.is_superuser || user.role === "admin" || user.role === "manager")) {
      throw redirect({ to: "/" })
    }
  },
  head: () => ({
    meta: [{ title: "Employees - FastAPI Template" }],
  }),
})

function EmployeesToolbar({
  departments,
  search,
  onChange,
}: {
  departments: DepartmentPublic[]
  search: z.infer<typeof searchSchema>
  onChange: (patch: Partial<z.infer<typeof searchSchema>>) => void
}) {
  return (
    <div className="grid gap-3 rounded-2xl border bg-card/80 p-4 shadow-sm backdrop-blur sm:grid-cols-2 xl:grid-cols-8">
      <div className="relative xl:col-span-2">
        <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          value={search.search}
          onChange={(e) => onChange({ search: e.target.value, page: 1 })}
          placeholder="Search name, email, department, role"
          className="pl-9"
        />
      </div>

      <Select
        value={search.departmentId || "all"}
        onValueChange={(value) =>
          onChange({ departmentId: value === "all" ? "" : value, page: 1 })
        }
      >
        <SelectTrigger className="w-full">
          <SelectValue placeholder="Department" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All departments</SelectItem>
          {departments.map((department) => (
            <SelectItem key={department.id} value={department.id}>
              {department.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Select
        value={search.status}
        onValueChange={(value) =>
          onChange({
            status: value as "all" | "active" | "inactive",
            page: 1,
          })
        }
      >
        <SelectTrigger className="w-full">
          <SelectValue placeholder="Status" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All statuses</SelectItem>
          <SelectItem value="active">Active</SelectItem>
          <SelectItem value="inactive">Inactive</SelectItem>
        </SelectContent>
      </Select>

      <Select
        value={search.role || "all"}
        onValueChange={(value) =>
          onChange({ role: value === "all" ? "" : value, page: 1 })
        }
      >
        <SelectTrigger className="w-full">
          <SelectValue placeholder="Role / Job" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All roles</SelectItem>
          <SelectItem value="manager">Manager</SelectItem>
          <SelectItem value="employee">Employee</SelectItem>
        </SelectContent>
      </Select>

      <Select
        value={search.sortBy}
        onValueChange={(value) =>
          onChange({
            sortBy: value as
              | "full_name"
              | "email"
              | "job_title"
              | "salary"
              | "created_at",
            page: 1,
          })
        }
      >
        <SelectTrigger className="w-full">
          <SelectValue placeholder="Sort by" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="created_at">Newest</SelectItem>
          <SelectItem value="full_name">Name</SelectItem>
          <SelectItem value="salary">Salary</SelectItem>
          <SelectItem value="email">Email</SelectItem>
          <SelectItem value="job_title">Role</SelectItem>
        </SelectContent>
      </Select>

      <Select
        value={search.sortOrder}
        onValueChange={(value) =>
          onChange({ sortOrder: value as "asc" | "desc", page: 1 })
        }
      >
        <SelectTrigger className="w-full">
          <SelectValue placeholder="Order" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="desc">Descending</SelectItem>
          <SelectItem value="asc">Ascending</SelectItem>
        </SelectContent>
      </Select>

      <Select
        value={`${search.size}`}
        onValueChange={(value) => onChange({ size: Number(value), page: 1 })}
      >
        <SelectTrigger className="w-full">
          <SelectValue placeholder="Page size" />
        </SelectTrigger>
        <SelectContent>
          {[5, 10, 25, 50].map((size) => (
            <SelectItem key={size} value={`${size}`}>
              {size} rows
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <div className="flex items-center justify-end">
        <Button
          type="button"
          variant="secondary"
          onClick={() =>
            onChange({
              search: "",
              departmentId: "",
              role: "",
              status: "all",
              sortBy: "created_at",
              sortOrder: "desc",
              page: 1,
              size: 10,
            })
          }
        >
          <X className="mr-2 size-4" />
          Clear
        </Button>
      </div>
    </div>
  )
}

function EmployeesTableContent() {
  const search = Route.useSearch()
  const navigate = useNavigate({ from: Route.fullPath })
  const { data: employees } = useSuspenseQuery(getEmployeesQueryOptions(search))
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

  const pageCount = employees.pages
  const pagination: PaginationState = {
    pageIndex: Math.max(search.page - 1, 0),
    pageSize: search.size,
  }

  const updateSearch = (patch: Partial<z.infer<typeof searchSchema>>) => {
    navigate({
      search: (current) => ({
        ...current,
        ...patch,
      }),
      replace: true,
    })
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div className="space-y-2">
          <h1 className="text-2xl font-bold tracking-tight">Employees</h1>
          <p className="text-muted-foreground">
            Search, filter, and manage employee records with server-side pagination.
          </p>
        </div>
        <AddEmployee departments={departments.data} />
      </div>

      <EmployeesToolbar
        departments={departments.data}
        search={search}
        onChange={updateSearch}
      />

      <div className="rounded-2xl border bg-card/80 shadow-sm backdrop-blur">
        <DataTable
          columns={columns(departments.data)}
          data={tableData}
          manualPagination
          pageCount={pageCount}
          pagination={pagination}
          onPaginationChange={(updater) => {
            const next =
              typeof updater === "function" ? updater(pagination) : updater
            updateSearch({
              page: next.pageIndex + 1,
              size: next.pageSize,
            })
          }}
          totalRows={employees.count}
        />
      </div>
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
