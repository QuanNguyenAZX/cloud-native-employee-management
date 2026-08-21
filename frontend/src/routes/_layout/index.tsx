import { useQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import {
  ArrowUpRight,
  Building2,
  ChartColumn,
  CircleDollarSign,
  Sparkles,
  Users,
  UserRound,
} from "lucide-react"
import type { ReactNode } from "react"

import { DashboardService } from "@/client"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"
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
    <Card className="group relative overflow-hidden border-white/10 bg-white/[0.04] p-0 shadow-[0_0_0_1px_rgba(255,255,255,0.04),0_16px_40px_rgba(0,0,0,0.28)] transition-all duration-200 hover:-translate-y-1 hover:border-white/16 hover:bg-white/[0.06] hover:shadow-[0_0_0_1px_rgba(255,255,255,0.08),0_20px_52px_rgba(0,0,0,0.34),0_0_36px_rgba(94,106,210,0.08)]">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(94,106,210,0.18),transparent_40%)] opacity-0 transition-opacity duration-200 group-hover:opacity-100" />
      <CardHeader className="relative flex flex-row items-start justify-between space-y-0 px-5 pt-5">
        <div className="space-y-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            {title}
          </CardTitle>
          <div className="flex items-end gap-2">
            <div className="text-3xl font-semibold tracking-[-0.04em] text-foreground">
              {value}
            </div>
            <ArrowUpRight className="mb-1 size-4 text-emerald-400/80 opacity-0 transition-opacity duration-200 group-hover:opacity-100" />
          </div>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/[0.05] p-3 text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.12)]">
          {icon}
        </div>
      </CardHeader>
      <CardContent className="relative px-5 pb-5">
        <p className="text-sm leading-relaxed text-muted-foreground">
          {description}
        </p>
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
    <Card className="overflow-hidden border-white/10 bg-white/[0.04] shadow-[0_0_0_1px_rgba(255,255,255,0.04),0_16px_40px_rgba(0,0,0,0.28)]">
      <CardHeader className="space-y-2 px-6 pt-6">
        <CardTitle className="text-xl font-semibold tracking-[-0.03em]">
          {title}
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          {subtitle}
        </p>
      </CardHeader>
      <CardContent className="px-6 pb-6">
        {data.length ? (
          <div className="space-y-4">
            {data.map((item) => (
              <div key={item.label} className="space-y-2">
                <div className="flex items-center justify-between gap-4 text-sm">
                  <span className="font-medium text-foreground">
                    {item.label}
                  </span>
                  <span className="rounded-full border border-white/10 bg-white/[0.04] px-2 py-0.5 text-xs text-muted-foreground">
                    {item.value}
                  </span>
                </div>
                <div className="h-2.5 overflow-hidden rounded-full bg-white/[0.05]">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-[#5E6AD2] via-sky-400 to-cyan-300 shadow-[0_0_16px_rgba(94,106,210,0.35)]"
                    style={{ width: `${(item.value / max) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex h-[280px] items-center justify-center rounded-3xl border border-dashed border-white/10 bg-white/[0.03] text-sm text-muted-foreground">
            No department data yet
          </div>
        )}
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
  const width = 720
  const height = 240
  const padding = 28

  if (!data.length) {
    return (
      <Card className="overflow-hidden border-white/10 bg-white/[0.04] shadow-[0_0_0_1px_rgba(255,255,255,0.04),0_16px_40px_rgba(0,0,0,0.28)]">
        <CardHeader className="space-y-2 px-6 pt-6">
          <CardTitle className="text-xl font-semibold tracking-[-0.03em]">
            {title}
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            {subtitle}
          </p>
        </CardHeader>
        <CardContent className="px-6 pb-6">
          <div className="flex h-[280px] items-center justify-center rounded-3xl border border-dashed border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.04),rgba(255,255,255,0.02))] text-sm text-muted-foreground">
            No growth data yet
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
    <Card className="overflow-hidden border-white/10 bg-white/[0.04] shadow-[0_0_0_1px_rgba(255,255,255,0.04),0_16px_40px_rgba(0,0,0,0.28)]">
      <CardHeader className="space-y-2 px-6 pt-6">
        <CardTitle className="text-xl font-semibold tracking-[-0.03em]">
          {title}
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          {subtitle}
        </p>
      </CardHeader>
      <CardContent className="px-4 pb-6 sm:px-6">
        <div className="overflow-hidden rounded-3xl border border-white/8 bg-[linear-gradient(180deg,rgba(255,255,255,0.04),rgba(255,255,255,0.02))]">
          <svg viewBox={`0 0 ${width} ${height}`} className="h-[280px] w-full">
            <defs>
              <linearGradient id="growthFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="rgb(94 106 210)" stopOpacity="0.38" />
                <stop offset="100%" stopColor="rgb(94 106 210)" stopOpacity="0.02" />
              </linearGradient>
            </defs>
            {[0.25, 0.5, 0.75].map((fraction) => (
              <line
                key={fraction}
                x1={padding}
                x2={width - padding}
                y1={padding + (height - padding * 2) * fraction}
                y2={padding + (height - padding * 2) * fraction}
                className="stroke-white/5"
                strokeDasharray="4 6"
              />
            ))}
            <path
              d={`${path} L ${points[points.length - 1]?.x ?? padding} ${height - padding} L ${padding} ${height - padding} Z`}
              fill="url(#growthFill)"
            />
            <path
              d={path}
              fill="none"
              stroke="rgb(104 114 217)"
              strokeWidth="3"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="drop-shadow-[0_0_18px_rgba(94,106,210,0.35)]"
            />
            {points.map((point) => (
              <g key={point.label}>
                <circle
                  cx={point.x}
                  cy={point.y}
                  r="4.5"
                  className="fill-[#ededef] stroke-[#5E6AD2] stroke-[2px]"
                />
                <text
                  x={point.x}
                  y={height - 10}
                  textAnchor="middle"
                  className="fill-muted-foreground text-[11px]"
                >
                  {point.label}
                </text>
              </g>
            ))}
          </svg>
        </div>
      </CardContent>
    </Card>
  )
}

function SummaryChip({
  label,
  value,
}: {
  label: string
  value: string | number
}) {
  return (
    <div className="rounded-2xl border border-white/8 bg-white/[0.04] px-4 py-3 shadow-[inset_0_1px_0_rgba(255,255,255,0.06)]">
      <div className="text-[11px] uppercase tracking-[0.24em] text-muted-foreground">
        {label}
      </div>
      <div className="mt-1 text-lg font-semibold tracking-[-0.03em] text-foreground">
        {value}
      </div>
    </div>
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
      <Card className="border-white/10 bg-white/[0.04] shadow-[0_0_0_1px_rgba(255,255,255,0.04),0_16px_40px_rgba(0,0,0,0.28)]">
        <CardHeader className="space-y-2 px-6 pt-6">
          <CardTitle className="text-xl font-semibold tracking-[-0.03em]">
            Dashboard temporarily unavailable
          </CardTitle>
        </CardHeader>
        <CardContent className="px-6 pb-6">
          <p className="text-sm leading-relaxed text-muted-foreground">
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

  const overview = [
    {
      label: "Employees",
      value: data.summary.total_employees,
    },
    {
      label: "Departments",
      value: data.summary.total_departments,
    },
    {
      label: "Managers",
      value: data.summary.total_managers,
    },
    {
      label: "Avg salary",
      value: formatCurrency(data.summary.average_salary),
    },
  ]

  return (
    <div className="space-y-6 text-foreground">
      <section className="relative overflow-hidden rounded-[30px] border border-white/10 bg-[linear-gradient(135deg,rgba(255,255,255,0.08),rgba(255,255,255,0.03)_45%,rgba(94,106,210,0.08))] p-6 shadow-[0_0_0_1px_rgba(255,255,255,0.04),0_24px_60px_rgba(0,0,0,0.34),0_0_60px_rgba(94,106,210,0.08)] backdrop-blur-xl sm:p-8">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(94,106,210,0.28),transparent_35%),radial-gradient(circle_at_bottom_left,rgba(56,189,248,0.1),transparent_28%)]" />
        <div className="relative grid gap-6 lg:grid-cols-[1.4fr_0.9fr]">
          <div className="space-y-5">
            <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.06] px-3 py-1 text-xs font-medium uppercase tracking-[0.24em] text-muted-foreground">
              <Sparkles className="size-3.5 text-[#6872D9]" />
              Operations overview
            </div>
            <div className="space-y-3">
              <h1 className="max-w-2xl text-4xl font-semibold tracking-[-0.05em] text-balance text-foreground sm:text-5xl">
                Hi, {currentUser?.full_name || currentUser?.email}
              </h1>
              <p className="max-w-2xl text-sm leading-7 text-muted-foreground sm:text-base">
                A calm, high-signal snapshot of your team. The layout is tuned for quick scanning,
                subtle depth, and clear hierarchy even when data is still sparse.
              </p>
            </div>
            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
              {overview.map((item) => (
                <SummaryChip
                  key={item.label}
                  label={item.label}
                  value={item.value}
                />
              ))}
            </div>
          </div>

          <div className="relative overflow-hidden rounded-[28px] border border-white/10 bg-[#09090c]/70 p-5 shadow-[0_0_0_1px_rgba(255,255,255,0.05),0_18px_44px_rgba(0,0,0,0.3)]">
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(94,106,210,0.16),transparent_45%)]" />
            <div className="relative space-y-4">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-muted-foreground">
                  Snapshot
                </p>
                <span className="rounded-full border border-emerald-400/20 bg-emerald-400/10 px-2.5 py-1 text-[11px] uppercase tracking-[0.2em] text-emerald-300">
                  Live
                </span>
              </div>
              <div className="rounded-2xl border border-white/8 bg-white/[0.04] p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs uppercase tracking-[0.22em] text-muted-foreground">
                      Focus
                    </p>
                    <p className="mt-2 text-lg font-semibold tracking-[-0.03em]">
                      Employee operations
                    </p>
                  </div>
                  <div className="rounded-2xl border border-white/10 bg-[#5E6AD2]/12 p-3 text-[#AEB6FF]">
                    <Users className="size-5" />
                  </div>
                </div>
                <div className="mt-4 space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">
                      Department coverage
                    </span>
                    <span className="font-medium text-foreground">
                      {data.summary.total_departments}
                    </span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-white/[0.05]">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-[#5E6AD2] via-sky-400 to-cyan-300"
                      style={{
                        width: `${Math.min(data.summary.total_departments * 25, 100)}%`,
                      }}
                    />
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">
                      Manager allocation
                    </span>
                    <span className="font-medium text-foreground">
                      {data.summary.total_managers}
                    </span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-white/[0.05]">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-fuchsia-400 via-[#5E6AD2] to-cyan-300"
                      style={{
                        width: `${Math.min(data.summary.total_managers * 25, 100)}%`,
                      }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          title="Total Employees"
          value={data.summary.total_employees}
          description="All employee records in the system"
          icon={<Users className="size-4" />}
        />
        <MetricCard
          title="Total Departments"
          value={data.summary.total_departments}
          description="Active department records"
          icon={<Building2 className="size-4" />}
        />
        <MetricCard
          title="Total Managers"
          value={data.summary.total_managers}
          description="Users assigned as managers"
          icon={<UserRound className="size-4" />}
        />
        <MetricCard
          title="Average Salary"
          value={formatCurrency(data.summary.average_salary)}
          description="Average across salary-enabled employees"
          icon={<CircleDollarSign className="size-4" />}
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

      <Card className="overflow-hidden border-white/10 bg-white/[0.04] shadow-[0_0_0_1px_rgba(255,255,255,0.04),0_16px_40px_rgba(0,0,0,0.28)]">
        <CardHeader className="space-y-2 px-6 pt-6">
          <CardTitle className="flex items-center gap-2 text-xl font-semibold tracking-[-0.03em]">
            <ChartColumn className="size-5 text-[#AEB6FF]" />
            Salary Distribution
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            Salary buckets give a quick view of payroll spread.
          </p>
        </CardHeader>
        <CardContent className="px-6 pb-6">
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {data.salary_distribution.map((item, index) => (
              <div
                key={item.label}
                className="group rounded-2xl border border-white/8 bg-white/[0.04] p-4 shadow-[inset_0_1px_0_rgba(255,255,255,0.06)] transition-all duration-200 hover:-translate-y-1 hover:border-white/12 hover:bg-white/[0.06]"
              >
                <div className="flex items-center justify-between">
                  <div className="text-sm font-medium text-foreground">
                    {item.label}
                  </div>
                  <div
                    className={cn(
                      "h-2.5 w-2.5 rounded-full shadow-[0_0_12px_currentColor]",
                      index % 4 === 0 && "bg-[#5E6AD2] text-[#5E6AD2]",
                      index % 4 === 1 && "bg-sky-400 text-sky-400",
                      index % 4 === 2 && "bg-cyan-300 text-cyan-300",
                      index % 4 === 3 && "bg-fuchsia-400 text-fuchsia-400",
                    )}
                  />
                </div>
                <div className="mt-3 text-3xl font-semibold tracking-[-0.04em] text-foreground">
                  {item.count}
                </div>
                <div className="mt-4 h-2 overflow-hidden rounded-full bg-white/[0.05]">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-[#5E6AD2] via-sky-400 to-cyan-300 shadow-[0_0_16px_rgba(94,106,210,0.35)]"
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
    <div className="space-y-6">
      <div className="h-[320px] animate-pulse rounded-[30px] border border-white/8 bg-white/[0.04] shadow-[0_0_0_1px_rgba(255,255,255,0.04)]" />
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <div
            key={index}
            className="h-36 animate-pulse rounded-2xl border border-white/8 bg-white/[0.04]"
          />
        ))}
      </div>
      <div className="grid gap-4 xl:grid-cols-2">
        <div className="h-[420px] animate-pulse rounded-2xl border border-white/8 bg-white/[0.04]" />
        <div className="h-[420px] animate-pulse rounded-2xl border border-white/8 bg-white/[0.04]" />
      </div>
      <div className="h-80 animate-pulse rounded-2xl border border-white/8 bg-white/[0.04]" />
    </div>
  )
}

function Dashboard() {
  return <DashboardContent />
}
