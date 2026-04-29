import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User } from '@/types/api'

interface AuthState {
  accessToken: string | null
  user: User | null
  setAuth: (token: string, user?: User | null) => void
  setUser: (user: User | null) => void
  clear: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      user: null,
      setAuth: (token, user = null) => set({ accessToken: token, user }),
      setUser: (user) => set({ user }),
      clear: () => set({ accessToken: null, user: null }),
    }),
    { name: 'auth' },
  ),
)

export function isTokenExpired(token: string | null): boolean {
  if (!token) return true
  try {
    const [, payload] = token.split('.')
    const decoded = JSON.parse(atob(payload))
    if (!decoded.exp) return false
    return decoded.exp * 1000 < Date.now()
  } catch {
    return true
  }
}
