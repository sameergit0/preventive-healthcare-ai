import axios, { type AxiosError } from 'axios'
import { useAuthStore } from '@/stores/authStore'
import type { ApiError } from '@/types/api'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((cfg) => {
  const token = useAuthStore.getState().accessToken
  if (token) {
    cfg.headers = cfg.headers ?? {}
    cfg.headers.Authorization = `Bearer ${token}`
  }
  return cfg
})

api.interceptors.response.use(
  (r) => r,
  (err: AxiosError<ApiError>) => {
    if (err.response?.status === 401) {
      const path = window.location.pathname
      if (path !== '/login' && path !== '/signup') {
        useAuthStore.getState().clear()
        window.location.href = '/login'
      }
    }
    return Promise.reject(err)
  },
)

export function getErrorMessage(err: unknown): string {
  if (axios.isAxiosError<ApiError>(err)) {
    const detail = err.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail) && detail.length > 0) return detail[0].msg
    return err.message
  }
  if (err instanceof Error) return err.message
  return 'Something went wrong'
}
