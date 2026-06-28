import { useQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Briefcase, Building2, UserRound, Users } from "lucide-react"

import {
  DepartmentsService,
  EmployeesService,
  ItemsService,
  UsersService,
} from "@/client"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import useAuth from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
  head: () => ({
    meta: [
      {
        title: "Dashboard - FastAPI Template",
      },
    ],
  }),
})

function Dashboard() {
  const { user: currentUser } = useAuth()
  const isAdmin = Boolean(
    currentUser?.is_superuser || currentUser?.role === "admin",
  )
  const isManagerOrAdmin = Boolean(isAdmin || currentUser?.role === "manager")

  const itemsQuery = useQuery({
    queryKey: ["dashboard", "items"],
    queryFn: () => ItemsService.readItems({ skip: 0, limit: 1 }),
    enabled: Boolean(currentUser),
  })
  const usersQuery = useQuery({
    queryKey: ["dashboard", "users"],
    queryFn: () => UsersService.readUsers({ skip: 0, limit: 1 }),
    enabled: isAdmin,
  })
  const departmentsQuery = useQuery({
    queryKey: ["dashboard", "departments"],
    queryFn: () => DepartmentsService.readDepartments({ page: 1, size: 1 }),
    enabled: isManagerOrAdmin,
  })
  const employeesQuery = useQuery({
    queryKey: ["dashboard", "employees"],
    queryFn: () => EmployeesService.readEmployees({ page: 1, size: 1 }),
    enabled: isAdmin,
  })

  return (
    <div className="flex flex-col gap-6">
      <div className="space-y-2">
        <h1 className="text-2xl font-bold tracking-tight truncate max-w-2xl">
          Hi, {currentUser?.full_name || currentUser?.email}
        </h1>
        <p className="text-muted-foreground">
          Welcome back. Here is the current pulse of the workspace.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Items</CardTitle>
            <Briefcase className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {itemsQuery.data?.count ?? 0}
            </div>
            <p className="text-xs text-muted-foreground">
              Visible in your account
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Users</CardTitle>
            <Users className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {isAdmin ? (usersQuery.data?.count ?? 0) : 1}
            </div>
            <p className="text-xs text-muted-foreground">
              {isAdmin ? "Registered accounts" : "Your account"}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Departments</CardTitle>
            <Building2 className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {isManagerOrAdmin ? (departmentsQuery.data?.count ?? 0) : "-"}
            </div>
            <p className="text-xs text-muted-foreground">
              {isManagerOrAdmin ? "Active department records" : "Admin only"}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Employees</CardTitle>
            <UserRound className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {isAdmin ? (employeesQuery.data?.count ?? 0) : "-"}
            </div>
            <p className="text-xs text-muted-foreground">
              {isAdmin ? "Total employee profiles" : "Admin only"}
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
