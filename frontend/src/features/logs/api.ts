import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { qk } from '@/lib/queryKeys'
import type { AllLogsResponse, DailyHealthLog, DailyHealthLogCreate } from '@/types/api'

export function useTodayLog() {
  return useQuery({
    queryKey: qk.logs.today,
    queryFn: async () => {
      const { data } = await api.get<AllLogsResponse>('/api/v1/metrics/daily-logs', {
        params: { request_type: 'today' },
      })
      return data
    },
  })
}

export function useAllLogs(page: number, limit: number, enabled = true) {
  return useQuery({
    queryKey: qk.logs.all(page, limit),
    queryFn: async () => {
      const { data } = await api.get<AllLogsResponse>('/api/v1/metrics/daily-logs', {
        params: { request_type: 'all', page, limit },
      })
      return data
    },
    enabled,
  })
}

export function useRangeLogs(start: string, end: string, page: number, limit: number, enabled = true) {
  return useQuery({
    queryKey: qk.logs.range(start, end, page, limit),
    queryFn: async () => {
      const { data } = await api.get<AllLogsResponse>('/api/v1/metrics/daily-logs', {
        params: { request_type: 'range', start_date: start, end_date: end, page, limit },
      })
      return data
    },
    enabled,
  })
}

function invalidateAll(qc: ReturnType<typeof useQueryClient>) {
  qc.invalidateQueries({ queryKey: ['logs'] })
  qc.invalidateQueries({ queryKey: ['analytics'] })
}

export function useUpsertTodayLog() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (body: DailyHealthLogCreate) => {
      const { data } = await api.post<DailyHealthLog>('/api/v1/metrics/daily-logs', body)
      return data
    },
    onSuccess: () => invalidateAll(qc),
  })
}

export function useUpdateLog(id: number) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (body: DailyHealthLogCreate) => {
      const { data } = await api.patch<DailyHealthLog>(`/api/v1/metrics/daily-logs/${id}`, body)
      return data
    },
    onSuccess: () => invalidateAll(qc),
  })
}

export function useDeleteToday() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async () => {
      await api.delete('/api/v1/metrics/daily-logs/today')
    },
    onSuccess: () => invalidateAll(qc),
  })
}

export function useDeleteLog() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/api/v1/metrics/daily-logs/${id}`)
    },
    onSuccess: () => invalidateAll(qc),
  })
}
