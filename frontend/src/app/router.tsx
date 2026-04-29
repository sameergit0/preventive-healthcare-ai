import { createBrowserRouter, Navigate } from 'react-router-dom'
import { AuthLayout } from '@/components/layout/AuthLayout'
import { AppLayout } from '@/components/layout/AppLayout'
import { ProtectedRoute, PublicOnlyRoute, RequireProfile } from './guards'
import { LoginPage } from '@/features/auth/LoginPage'
import { SignupPage } from '@/features/auth/SignupPage'
import { ProfileCreatePage } from '@/features/profile/ProfileCreatePage'
import { ProfileEditPage } from '@/features/profile/ProfileEditPage'
import { LogTodayPage } from '@/features/logs/LogTodayPage'
import { HistoryPage } from '@/features/logs/HistoryPage'
import { DashboardPage } from '@/features/dashboard/DashboardPage'
import { AnalyticsPage } from '@/features/analytics/AnalyticsPage'

export const router = createBrowserRouter([
  {
    element: <PublicOnlyRoute />,
    children: [
      {
        element: <AuthLayout />,
        children: [
          { path: '/login', element: <LoginPage /> },
          { path: '/signup', element: <SignupPage /> },
        ],
      },
    ],
  },
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <AuthLayout />,
        children: [
          { path: '/profile/create', element: <ProfileCreatePage /> },
        ],
      },
      {
        element: <AppLayout />,
        children: [
          { path: '/profile/edit', element: <ProfileEditPage /> },
          {
            element: <RequireProfile />,
            children: [
              { path: '/dashboard', element: <DashboardPage /> },
              { path: '/log', element: <LogTodayPage /> },
              { path: '/history', element: <HistoryPage /> },
              { path: '/analytics', element: <AnalyticsPage /> },
            ],
          },
        ],
      },
    ],
  },
  { path: '/', element: <Navigate to="/dashboard" replace /> },
  { path: '*', element: <Navigate to="/dashboard" replace /> },
])
