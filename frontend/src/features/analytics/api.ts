import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { qk } from '@/lib/queryKeys'
import type {
  OverallSummaryResponse,
  InsightsResponse,
  TrendsResponse,
  RecommendationsResponse,
  HealthStatusResponse,
} from '@/types/api'

export function useSummary(start: string, end: string, enabled = true) {
  return useQuery({
    queryKey: qk.analytics.summary(start, end),
    queryFn: async () => {
      const { data } = await api.get<OverallSummaryResponse>('/api/v1/analytics/summary', {
        params: { start_date: start, end_date: end },
      })
      return data
    },
    enabled,
  })
}

export function useInsights(enabled = true) {
  return useQuery({
    queryKey: qk.analytics.insights,
    queryFn: async () => {
      const { data } = await api.get<InsightsResponse>('/api/v1/analytics/insights')
      return data
    },
    enabled,
  })
}

export function useTrends(start: string, end: string, enabled = true) {
  return useQuery({
    queryKey: qk.analytics.trends(start, end),
    queryFn: async () => {
      const { data } = await api.get<TrendsResponse>('/api/v1/analytics/trends', {
        params: { start_date: start, end_date: end },
      })
      return data
    },
    enabled,
  })
}

export function useRecommendations(enabled = true) {
  return useQuery({
    queryKey: qk.analytics.recommendations,
    queryFn: async () => {
      const { data } = await api.get<RecommendationsResponse>('/api/v1/analytics/recommendations')
      return data
    },
    enabled,
  })
}

export function useStatus(enabled = true) {
  return useQuery({
    queryKey: qk.analytics.status,
    queryFn: async () => {
      const { data } = await api.get<HealthStatusResponse>('/api/v1/analytics/status')
      return data
    },
    enabled,
  })
}
