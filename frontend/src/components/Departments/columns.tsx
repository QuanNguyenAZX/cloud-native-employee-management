import type { ColumnDef } from "@tanstack/react-table"

import type { DepartmentPublic } from "@/client"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import { DepartmentActionsMenu } from "./DepartmentActionsMenu"

export const columns: ColumnDef<DepartmentPublic>[] = [
  {
    accessorKey: "name",
    header: "Name",
    cell: ({ row }) => <span className="font-medium">{row.original.name}</span>,
  },
  {
    accessorKey: "description",
    header: "Description",
    cell: ({ row }) => (
      <span className={cn("text-muted-foreground", !row.original.description && "italic")}>
        {row.original.description || "No description"}
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
        <DepartmentActionsMenu department={row.original} />
      </div>
    ),
  },
]
