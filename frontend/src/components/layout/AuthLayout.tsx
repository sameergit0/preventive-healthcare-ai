import { Outlet } from 'react-router-dom'
import { Activity } from 'lucide-react'

export function AuthLayout() {
  return (
    <div className="min-h-svh bg-background">
      <div className="mx-auto flex min-h-svh max-w-md flex-col px-margin py-lg">
        <div className="mb-lg flex items-center gap-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-primary-on">
            <Activity className="h-5 w-5" />
          </div>
          <span className="text-headline-md font-heading font-bold text-on-surface">Vitality</span>
        </div>
        <Outlet />
      </div>
    </div>
  )
}
