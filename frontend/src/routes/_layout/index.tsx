import { useQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import {
  Building2,
  ChartColumn,
  CircleDollarSign,
  Users,
  UserRound,
} from "lucide-react"
import { type ReactNode } from "react"

import { DashboardService } from "@/client"
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

function getDashboardQueryOptions() {
  return {
    queryFn: () => DashboardService.readDashboard(),
    queryKey: ["dashboard"],
  }
}

function formatCurrency(value: number | null | undefined) {
  if (value === null || value === undefined) return "-"
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value)
}

function MetricCard({
  title,
  value,
  description,
  icon,
}: {
  title: string
  value: string | number
  description: string
  icon: ReactNode
}) {
  return (
    <Card className="overflow-hidden border-border/60 bg-card/80 shadow-sm backdrop-blur">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        {icon}
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-bold tracking-tight">{value}</div>
        <p className="text-xs text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  )
}

function MiniBarChart({
  title,
  subtitle,
  data,
}: {
  title: string
  subtitle: string
  data: Array<{ label: string; value: number }>
}) {
  const max = Math.max(...data.map((item) => item.value), 1)
  return (
    <Card className="border-border/60 bg-card/80 shadow-sm backdrop-blur">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <p className="text-sm text-muted-foreground">{subtitle}</p>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {data.map((item) => (
            <div key={item.label} className="space-y-1">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium">{item.label}</span>
                <span className="text-muted-foreground">{item.value}</span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-muted">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-emerald-500 via-sky-500 to-indigo-500"
                  style={{ width: `${(item.value / max) * 100}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

function LineChart({
  title,
  subtitle,
  data,
}: {
  title: string
  subtitle: string
  data: Array<{ label: string; value: number }>
}) {
  const width = 640
  const height = 240
  const padding = 24
  if (!data.length) {
    return (
      <Card className="border-border/60 bg-card/80 shadow-sm backdrop-blur">
        <CardHeader>
          <CardTitle>{title}</CardTitle>
          <p className="text-sm text-muted-foreground">{subtitle}</p>
        </CardHeader>
        <CardContent>
          <div className="flex h-64 items-center justify-center rounded-2xl border border-dashed text-sm text-muted-foreground">
            No data yet
          </div>
        </CardContent>
      </Card>
    )
  }
  const max = Math.max(...data.map((item) => item.value), 1)
  const stepX = data.length > 1 ? (width - padding * 2) / (data.length - 1) : 0
  const points = data.map((item, index) => {
    const x = padding + stepX * index
    const y = height - padding - ((height - padding * 2) * item.value) / max
    return { x, y, ...item }
  })
  const path = points
    .map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`)
    .join(" ")

  return (
    <Card className="border-border/60 bg-card/80 shadow-sm backdrop-blur">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <p className="text-sm text-muted-foreground">{subtitle}</p>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <svg viewBox={`0 0 ${width} ${height}`} className="h-64 w-full">
            <defs>
              <linearGradient id="growthFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="rgb(34 197 94)" stopOpacity="0.35" />
                <stop offset="100%" stopColor="rgb(59 130 246)" stopOpacity="0.02" />
              </linearGradient>
            </defs>
            <path
              d={`${path} L ${points[points.length - 1]?.x ?? padding} ${height - padding} L ${padding} ${height - padding} Z`}
              fill="url(#growthFill)"
            />
            <path d={path} fill="none" stroke="currentColor" strokeWidth="3" className="text-sky-500" />
            {points.map((point) => (
              <g key={point.label}>
                <circle cx={point.x} cy={point.y} r="4" className="fill-emerald-500" />
                <text
                  x={point.x}
                  y={height - 8}
                  textAnchor="middle"
                  className="fill-muted-foreground text-[11px]"
                >
                  {point.label}
                </text>
                <text
                  x={point.x}
                  y={point.y - 10}
                  textAnchor="middle"
                  className="fill-foreground text-[11px] font-semibold"
                >
                  {point.value}
                </text>
              </g>
            ))}
          </svg>
        </div>
      </CardContent>
    </Card>
  )
}

function DashboardContent() {
  const { user: currentUser } = useAuth()
  const dashboardQuery = useQuery({
    ...getDashboardQueryOptions(),
    enabled: Boolean(currentUser),
  })

  if (!currentUser || dashboardQuery.isLoading) {
    return <DashboardSkeleton />
  }

  if (dashboardQuery.isError) {
    return (
      <Card className="border-border/60 bg-card/80 shadow-sm backdrop-blur">
        <CardHeader>
          <CardTitle>Dashboard temporarily unavailable</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            We could not load dashboard data right now. Please refresh or try again later.
          </p>
        </CardContent>
      </Card>
    )
  }

  const data = dashboardQuery.data
  if (!data) {
    return <DashboardSkeleton />
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="space-y-2">
        <h1 className="max-w-2xl truncate text-2xl font-bold tracking-tight">
          Hi, {currentUser?.full_name || currentUser?.email}
        </h1>
        <p className="text-muted-foreground">
          Here is the operational overview for your team.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          title="Total Employees"
          value={data.summary.total_employees}
          description="All employee records in the system"
          icon={<Users className="size-4 text-muted-foreground" />}
        />
        <MetricCard
          title="Total Departments"
          value={data.summary.total_departments}
          description="Active department records"
          icon={<Building2 className="size-4 text-muted-foreground" />}
        />
        <MetricCard
          title="Total Managers"
          value={data.summary.total_managers}
          description="Users assigned as managers"
          icon={<UserRound className="size-4 text-muted-foreground" />}
        />
        <MetricCard
          title="Average Salary"
          value={formatCurrency(data.summary.average_salary)}
          description="Average across salary-enabled employees"
          icon={<CircleDollarSign className="size-4 text-muted-foreground" />}
        />
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <MiniBarChart
          title="Employee by Department"
          subtitle="Distribution across department groups"
          data={data.employee_by_department.map((item) => ({
            label: item.department_name,
            value: item.count,
          }))}
        />
        <LineChart
          title="Employee Growth"
          subtitle="New employee records by month"
          data={data.employee_growth.map((item) => ({
            label: item.period,
            value: item.count,
          }))}
        />
      </div>

      <Card className="border-border/60 bg-card/80 shadow-sm backdrop-blur">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ChartColumn className="size-5 text-muted-foreground" />
            Salary Distribution
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            Salary buckets give a quick view of payroll spread.
          </p>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {data.salary_distribution.map((item) => (
              <div
                key={item.label}
                className="rounded-2xl border bg-background/70 p-4 shadow-sm"
              >
                <div className="text-sm font-medium">{item.label}</div>
                <div className="mt-2 text-3xl font-bold">{item.count}</div>
                <div className="mt-4 h-2 overflow-hidden rounded-full bg-muted">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-amber-500 to-rose-500"
                    style={{
                      width: `${Math.min(item.count * 20, 100)}%`,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
function DashboardSkeleton() {
  return (
    <div className="flex flex-col gap-6">
      <div className="space-y-2">
        <div className="h-8 w-64 animate-pulse rounded bg-muted" />
        <div className="h-4 w-96 animate-pulse rounded bg-muted" />
      </div>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <div
            key={index}
            className="h-32 animate-pulse rounded-2xl border bg-muted/50"
          />
        ))}
      </div>
      <div className="grid gap-4 xl:grid-cols-2">
        <div className="h-80 animate-pulse rounded-2xl border bg-muted/50" />
        <div className="h-80 animate-pulse rounded-2xl border bg-muted/50" />
      </div>
      <div className="h-72 animate-pulse rounded-2xl border bg-muted/50" />
    </div>
  )
}

function Dashboard() {
  return <DashboardContent />
}
