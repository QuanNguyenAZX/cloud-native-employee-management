import { createFileRoute, redirect } from "@tanstack/react-router"

export const Route = createFileRoute("/_layout/dashboard")({
  beforeLoad: () => {
    throw redirect({
      to: "/",
    })
  },
})
