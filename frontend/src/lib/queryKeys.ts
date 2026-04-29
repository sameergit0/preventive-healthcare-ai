export const qk = {
  me: ['me'] as const,
  timezones: ['timezones'] as const,
  profile: ['profile'] as const,
  logs: {
    today: ['logs', 'today'] as const,
    all: (page: number, limit: number) => ['logs', 'all', page, limit] as const,
    range: (start: string, end: string, page: number, limit: number) =>
      ['logs', 'range', start, end, page, limit] as const,
  },
  analytics: {
    summary: (s: string, e: string) => ['analytics', 'summary', s, e] as const,
    insights: (s: string, e: string) => ['analytics', 'insights', s, e] as const,
    trends: (s: string, e: string) => ['analytics', 'trends', s, e] as const,
    recommendations: (s: string, e: string) => ['analytics', 'recommendations', s, e] as const,
    scoreHistory: (s: string, e: string, includeEmpty: boolean) =>
      ['analytics', 'score-history', s, e, includeEmpty] as const,
  },
}
