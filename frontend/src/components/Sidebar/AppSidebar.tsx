import { Briefcase, Building2, Home, Users } from "lucide-react"

import { SidebarAppearance } from "@/components/Common/Appearance"
import { Logo } from "@/components/Common/Logo"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
} from "@/components/ui/sidebar"
import useAuth from "@/hooks/useAuth"
import { type Item, Main } from "./Main"
import { User } from "./User"

const baseItems: Item[] = [
  { icon: Home, title: "Dashboard", path: "/" },
  { icon: Briefcase, title: "Items", path: "/items" },
]

export function AppSidebar() {
  const { user: currentUser } = useAuth()
  const isAdmin = Boolean(
    currentUser?.is_superuser || currentUser?.role === "admin",
  )
  const canViewDepartments = Boolean(isAdmin || currentUser?.role === "manager")

  const items = [
    ...baseItems,
    ...(canViewDepartments
      ? [{ icon: Building2, title: "Departments", path: "/departments" }]
      : []),
    ...(isAdmin
      ? [{ icon: Users, title: "Employees", path: "/employees" }]
      : []),
    ...(isAdmin ? [{ icon: Users, title: "Admin", path: "/admin" }] : []),
  ]

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="border-b border-white/8 px-4 py-5 group-data-[collapsible=icon]:items-center group-data-[collapsible=icon]:px-0">
        <Logo variant="responsive" />
      </SidebarHeader>
      <SidebarContent className="px-2 py-3">
        <Main items={items} />
      </SidebarContent>
      <SidebarFooter className="border-t border-white/8 p-3">
        <SidebarAppearance />
        <User user={currentUser} />
      </SidebarFooter>
    </Sidebar>
  )
}

export default AppSidebar
