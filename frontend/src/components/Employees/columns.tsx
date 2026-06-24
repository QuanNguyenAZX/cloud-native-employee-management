import type { ColumnDef } from "@tanstack/react-table"

import type { DepartmentPublic, EmployeePublic } from "@/client"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import { EmployeeActionsMenu } from "./EmployeeActionsMenu"

export type EmployeeTableData = EmployeePublic & {
  department_name: string
}

export const columns = (departments: DepartmentPublic[]): ColumnDef<EmployeeTableData>[] => [
  {
    accessorKey: "full_name",
    header: "Full Name",
    cell: ({ row }) => <span className="font-medium">{row.original.full_name}</span>,
  },
  {
    accessorKey: "email",
    header: "Email",
    cell: ({ row }) => <span className="text-muted-foreground">{row.original.email}</span>,
  },
  {
    accessorKey: "job_title",
    header: "Job Title",
  },
  {
    accessorKey: "department_name",
    header: "Department",
    cell: ({ row }) => (
      <span className={cn(!row.original.department_name && "italic text-muted-foreground")}>
        {row.original.department_name || "Unknown"}
      </span>
    ),
  },
  {
    accessorKey: "is_active",
    header: "Status",
    cell: ({ row }) => (
      <Badge variant={row.original.is_active ? "default" : "secondary"}>
        {row.original.is_active ? "Active" : "Inactive"}
      </Badge>
    ),
  },
  {
    id: "actions",
    header: () => <span className="sr-only">Actions</span>,
    cell: ({ row }) => (
      <div className="flex justify-end">
        <EmployeeActionsMenu employee={row.original} departments={departments} />
      </div>
    ),
  },
]
