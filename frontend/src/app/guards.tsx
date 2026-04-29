import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuthStore, isTokenExpired } from '@/stores/authStore'
import { useProfile } from '@/features/profile/api'
import { Spinner } from '@/components/ui/Spinner'

export function ProtectedRoute() {
  const token = useAuthStore((s) => s.accessToken)
  const location = useLocation()
  if (!token || isTokenExpired(token)) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }
  return <Outlet />
}

export function PublicOnlyRoute() {
  const token = useAuthStore((s) => s.accessToken)
  if (token && !isTokenExpired(token)) {
    return <Navigate to="/dashboard" replace />
  }
  return <Outlet />
}

export function RequireProfile() {
  const { data, isLoading } = useProfile()
  if (isLoading) {
    return (
      <div className="flex min-h-svh items-center justify-center">
        <Spinner />
      </div>
    )
  }
  if (data && data.profile === null) {
    return <Navigate to="/profile/create" replace />
  }
  return <Outlet />
}
