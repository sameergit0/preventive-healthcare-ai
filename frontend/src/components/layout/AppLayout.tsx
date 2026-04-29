import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { Activity, BarChart3, ClipboardList, History, Home, LogOut, User as UserIcon } from 'lucide-react'
import { useAuthStore } from '@/stores/authStore'
import { useProfile } from '@/features/profile/api'
import { Avatar } from '@/components/ui/Avatar'
import { cn } from '@/lib/utils'
import { useState } from 'react'

const items = [
  { to: '/dashboard', label: 'Dashboard', icon: Home },
  { to: '/log', label: 'Log Today', icon: ClipboardList },
  { to: '/history', label: 'History', icon: History },
  { to: '/analytics', label: 'Analytics', icon: BarChart3 },
]

export function AppLayout() {
  const clear = useAuthStore((s) => s.clear)
  const navigate = useNavigate()
  const { data } = useProfile()
  const profile = data?.profile
  const [menuOpen, setMenuOpen] = useState(false)

  const logout = () => {
    clear()
    navigate('/login', { replace: true })
  }

  return (
    <div className="min-h-svh bg-background">
      {/* Top bar */}
      <header className="sticky top-0 z-30 border-b border-outline-variant/40 bg-background/90 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-margin">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-primary-on">
                <Activity className="h-5 w-5" />
              </div>
              <span className="text-headline-md font-heading font-bold text-on-surface hidden sm:inline">Vitality</span>
            </div>
            <nav className="hidden md:flex items-center gap-1">
              {items.map(({ to, label, icon: Icon }) => (
                <NavLink
                  key={to}
                  to={to}
                  className={({ isActive }) =>
                    cn(
                      'flex items-center gap-2 rounded-lg px-3 py-2 text-body-md font-medium transition-colors',
                      isActive
                        ? 'bg-primary-fixed text-on-primary-fixed'
                        : 'text-on-surface-variant hover:bg-surface-container',
                    )
                  }
                >
                  <Icon className="h-4 w-4" />
                  {label}
                </NavLink>
              ))}
            </nav>
          </div>
          <div className="relative">
            <button
              onClick={() => setMenuOpen((v) => !v)}
              className="flex items-center gap-2 rounded-full p-1 hover:bg-surface-container"
              aria-label="Profile menu"
            >
              <Avatar src={profile?.profile_image} name={profile?.full_name} size={36} />
            </button>
            {menuOpen && (
              <>
                <div className="fixed inset-0 z-10" onClick={() => setMenuOpen(false)} />
                <div className="absolute right-0 top-full z-20 mt-2 w-56 overflow-hidden rounded-lg bg-surface-container-lowest shadow-level-2">
                  <div className="border-b border-outline-variant/30 px-4 py-3">
                    <p className="text-body-md font-semibold text-on-surface truncate">{profile?.full_name ?? 'Welcome'}</p>
                  </div>
                  <button
                    onClick={() => { setMenuOpen(false); navigate('/profile/edit') }}
                    className="flex w-full items-center gap-2 px-4 py-2.5 text-left text-body-md text-on-surface hover:bg-surface-container"
                  >
                    <UserIcon className="h-4 w-4" /> Edit profile
                  </button>
                  <button
                    onClick={logout}
                    className="flex w-full items-center gap-2 px-4 py-2.5 text-left text-body-md text-error hover:bg-error-container/40"
                  >
                    <LogOut className="h-4 w-4" /> Log out
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="mx-auto max-w-7xl px-margin pb-24 pt-md md:pb-lg">
        <Outlet />
      </main>

      {/* Bottom nav (mobile) */}
      <nav className="fixed bottom-0 left-0 right-0 z-30 border-t border-outline-variant/40 bg-surface-container-lowest md:hidden">
        <div className="mx-auto flex max-w-md justify-around">
          {items.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                cn(
                  'flex flex-1 flex-col items-center gap-1 py-2 text-label-md',
                  isActive ? 'text-primary' : 'text-on-surface-variant',
                )
              }
            >
              <Icon className="h-5 w-5" />
              {label}
            </NavLink>
          ))}
        </div>
      </nav>
    </div>
  )
}
