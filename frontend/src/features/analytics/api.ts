import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { qk } from '@/lib/queryKeys'
import type {
  HealthInsightsResponse,
  HealthRecommendationsResponse,
  HealthScoreHistoryResponse,
  HealthSummaryResponse,
  HealthTrendsResponse,
} from '@/types/api'

const params = (start_date: string, end_date: string) => ({ start_date, end_date })

export function useSummary(start: string, end: string, enabled = true) {
  return useQuery({
    queryKey: qk.analytics.summary(start, end),
    queryFn: async () => {
      const { data } = await api.get<HealthSummaryResponse>('/api/v1/analytics/summary', {
        params: params(start, end),
      })
      return data
    },
    enabled,
  })
}

export function useInsights(start: string, end: string, enabled = true) {
  return useQuery({
    queryKey: qk.analytics.insights(start, end),
    queryFn: async () => {
      const { data } = await api.get<HealthInsightsResponse>('/api/v1/analytics/insights', {
        params: params(start, end),
      })
      return data
    },
    enabled,
  })
}

export function useTrends(start: string, end: string, enabled = true) {
  return useQuery({
    queryKey: qk.analytics.trends(start, end),
    queryFn: async () => {
      const { data } = await api.get<HealthTrendsResponse>('/api/v1/analytics/trends', {
        params: params(start, end),
      })
      return data
    },
    enabled,
  })
}

export function useRecommendations(start: string, end: string, enabled = true) {
  return useQuery({
    queryKey: qk.analytics.recommendations(start, end),
    queryFn: async () => {
      const { data } = await api.get<HealthRecommendationsResponse>(
        '/api/v1/analytics/recommendations',
        { params: params(start, end) },
      )
      return data
    },
    enabled,
  })
}

export function useScoreHistory(start: string, end: string, includeEmpty = false, enabled = true) {
  return useQuery({
    queryKey: qk.analytics.scoreHistory(start, end, includeEmpty),
    queryFn: async () => {
      const { data } = await api.get<HealthScoreHistoryResponse>(
        '/api/v1/analytics/score-history',
        { params: { ...params(start, end), include_empty: includeEmpty } },
      )
      return data
    },
    enabled,
  })
}
