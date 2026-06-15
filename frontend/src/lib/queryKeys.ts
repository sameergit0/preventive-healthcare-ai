export const qk = {
  me: ['me'] as const,
  timezones: ['timezones'] as const,
  profile: ['profile'] as const,
  lifestyle: ['lifestyle'] as const,
  medicalHistory: ['medical-history'] as const,
  logs: {
    today: ['logs', 'today'] as const,
    all: (page: number, limit: number) => ['logs', 'all', page, limit] as const,
    range: (start: string, end: string, page: number, limit: number) =>
      ['logs', 'range', start, end, page, limit] as const,
  },
  analytics: {
    summary: (s: string, e: string) => ['analytics', 'summary', s, e] as const,
    insights: ['analytics', 'insights'] as const,
    trends: (s: string, e: string) => ['analytics', 'trends', s, e] as const,
    recommendations: ['analytics', 'recommendations'] as const,
    status: ['analytics', 'status'] as const,
  },
}
