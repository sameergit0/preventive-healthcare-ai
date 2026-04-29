import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { qk } from '@/lib/queryKeys'
import { useAuthStore } from '@/stores/authStore'
import type { LoginRequest, SignupRequest, TokenResponse, TimezonesResponse, User } from '@/types/api'

export function useSignup() {
  return useMutation({
    mutationFn: async (body: SignupRequest) => {
      const { data } = await api.post('/api/v1/auth/signup', body)
      return data
    },
  })
}

export function useLogin() {
  const setAuth = useAuthStore((s) => s.setAuth)
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (body: LoginRequest) => {
      const { data } = await api.post<TokenResponse>('/api/v1/auth/login', body)
      return data
    },
    onSuccess: (data) => {
      setAuth(data.access_token)
      qc.invalidateQueries({ queryKey: qk.me })
    },
  })
}

export function useMe(enabled = true) {
  const setUser = useAuthStore((s) => s.setUser)
  return useQuery({
    queryKey: qk.me,
    queryFn: async () => {
      const { data } = await api.get<User>('/api/v1/auth/me')
      setUser(data)
      return data
    },
    enabled,
    staleTime: 5 * 60_000,
  })
}

export function useTimezones() {
  return useQuery({
    queryKey: qk.timezones,
    queryFn: async () => {
      const { data } = await api.get<TimezonesResponse>('/api/v1/timezones/')
      return data
    },
    staleTime: 24 * 60 * 60_000,
  })
}
