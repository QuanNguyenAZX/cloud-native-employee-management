import { createFileRoute, Outlet, redirect } from "@tanstack/react-router"

import { Footer } from "@/components/Common/Footer"
import AppSidebar from "@/components/Sidebar/AppSidebar"
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar"
import { isLoggedIn } from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout")({
  component: Layout,
  beforeLoad: async () => {
    if (!isLoggedIn()) {
      throw redirect({
        to: "/login",
      })
    }
  },
})

function Layout() {
  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset className="relative overflow-hidden bg-[radial-gradient(ellipse_at_top,#0f1120_0%,#070709_45%,#050506_100%)]">
        <div className="pointer-events-none absolute inset-0 overflow-hidden">
          <div className="animate-float-slow absolute -top-56 left-1/2 h-[34rem] w-[34rem] -translate-x-1/2 rounded-full bg-[#5E6AD2]/18 blur-[140px]" />
          <div className="animate-float-slower absolute top-24 -left-32 h-[24rem] w-[24rem] rounded-full bg-cyan-400/10 blur-[110px]" />
          <div className="animate-glow-pulse absolute bottom-0 right-0 h-[20rem] w-[20rem] rounded-full bg-fuchsia-500/8 blur-[120px]" />
          <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:72px_72px] opacity-[0.035]" />
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_0,transparent_55%,rgba(5,5,6,0.55)_100%)]" />
        </div>
        <header className="sticky top-0 z-20 flex h-16 shrink-0 items-center justify-between gap-4 border-b border-white/8 bg-[#050506]/78 px-4 backdrop-blur-xl sm:px-6">
          <div className="flex items-center gap-3">
            <SidebarTrigger className="-ml-1 text-muted-foreground transition-colors hover:text-foreground" />
            <div className="hidden items-center gap-2 rounded-full border border-white/8 bg-white/[0.03] px-3 py-1 text-xs text-muted-foreground sm:flex">
              <span className="size-1.5 rounded-full bg-emerald-400 shadow-[0_0_12px_rgba(74,222,128,0.65)]" />
              Live workspace
            </div>
          </div>
          <div className="hidden items-center gap-2 rounded-full border border-white/8 bg-white/[0.03] px-3 py-1 text-xs text-muted-foreground md:flex">
            FastAPI operations
          </div>
        </header>
        <main className="relative z-10 flex-1 p-4 sm:p-6 lg:p-8">
          <div className="mx-auto w-full max-w-7xl">
            <Outlet />
          </div>
        </main>
        <Footer />
      </SidebarInset>
    </SidebarProvider>
  )
}

export default Layout
