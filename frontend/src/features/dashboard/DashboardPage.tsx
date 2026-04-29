import { useMemo } from 'react'
import { Link } from 'react-router-dom'
import { format, subDays } from 'date-fns'
import { Footprints, Moon, Droplet, ArrowRight, Sparkles } from 'lucide-react'
import { LineChart, Line, ResponsiveContainer, XAxis, YAxis, Tooltip } from 'recharts'
import { Card } from '@/components/ui/Card'
import { ProgressRing } from '@/components/ui/ProgressRing'
import { Skeleton } from '@/components/ui/Skeleton'
import { useProfile } from '@/features/profile/api'
import { useTodayLog } from '@/features/logs/api'
import { useRecommendations, useScoreHistory, useSummary } from '@/features/analytics/api'
import { formatNumber } from '@/lib/utils'

const TARGETS = { steps: 10000, sleep: 7.5, water: 2.7 }

export function DashboardPage() {
  const { data: profile } = useProfile()
  const today = useTodayLog()
  const end = format(new Date(), 'yyyy-MM-dd')
  const start7 = format(subDays(new Date(), 6), 'yyyy-MM-dd')

  const summary = useSummary(start7, end)
  const recos = useRecommendations(start7, end)
  const scores = useScoreHistory(start7, end, true)

  const log = today.data?.logs[0]
  const todayScore = useMemo(() => {
    const entry = scores.data?.scores.find((s) => s.date === end)
    return entry?.score ?? null
  }, [scores.data, end])
  const topReco = useMemo(() => {
    const order: Record<string, number> = { high: 0, medium: 1, low: 2 }
    return recos.data?.recommendations.slice().sort((a, b) => order[a.priority] - order[b.priority])[0]
  }, [recos.data])

  const greeting = useMemo(() => {
    const h = new Date().getHours()
    if (h < 12) return 'Good morning'
    if (h < 18) return 'Good afternoon'
    return 'Good evening'
  }, [])
  const firstName = profile?.profile?.full_name.split(' ')[0] ?? ''

  return (
    <div className="flex flex-col gap-md">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-headline-xl text-on-surface">{greeting}, {firstName}</h1>
          <p className="mt-1 text-body-md text-on-surface-variant">Here's your wellness snapshot.</p>
        </div>
        <Link
          to="/log"
          className="inline-flex h-11 items-center gap-2 rounded-lg bg-primary px-4 text-body-md font-semibold text-primary-on hover:bg-primary-container"
        >
          Log today <ArrowRight className="h-4 w-4" />
        </Link>
      </div>

      {/* Top row */}
      <div className="grid grid-cols-1 gap-md md:grid-cols-4">
        <Card className="flex items-center gap-md md:col-span-1">
          <ProgressRing value={todayScore ?? 0} size={96} stroke={10} fillClassName="text-primary">
            <div className="text-center">
              <p className="text-headline-md text-on-surface">{todayScore ?? '—'}</p>
              <p className="text-label-md text-on-surface-variant">today</p>
            </div>
          </ProgressRing>
          <div>
            <p className="text-label-lg uppercase text-on-surface-variant">Score</p>
            <p className="text-body-md text-on-surface">Composite of steps, sleep, water</p>
          </div>
        </Card>
        <MetricCard
          icon={<Footprints className="h-5 w-5" />}
          label="Steps"
          value={log?.steps ?? null}
          target={TARGETS.steps}
          unit=""
          formatValue={(v) => formatNumber(v)}
        />
        <MetricCard
          icon={<Moon className="h-5 w-5" />}
          label="Sleep"
          value={log?.sleep_hours ?? null}
          target={TARGETS.sleep}
          unit="h"
          formatValue={(v) => v.toFixed(1)}
        />
        <MetricCard
          icon={<Droplet className="h-5 w-5" />}
          label="Water"
          value={log?.water_intake ?? null}
          target={TARGETS.water}
          unit="L"
          formatValue={(v) => v.toFixed(1)}
        />
      </div>

      <div className="grid grid-cols-1 gap-md lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <div className="flex items-center justify-between">
            <h3 className="text-headline-md text-on-surface">7-day score</h3>
            <Link to="/analytics" className="text-body-sm text-primary hover:underline">View analytics</Link>
          </div>
          <div className="mt-3 h-48">
            {scores.isLoading ? (
              <Skeleton className="h-full" />
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={scores.data?.scores ?? []}>
                  <XAxis dataKey="date" tickFormatter={(d) => format(new Date(d), 'EEE')} stroke="#737686" fontSize={12} />
                  <YAxis domain={[0, 100]} stroke="#737686" fontSize={12} />
                  <Tooltip />
                  <Line type="monotone" dataKey="score" stroke="#004ac6" strokeWidth={3} dot={{ r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
        </Card>

        <Card className="flex flex-col gap-3">
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-tertiary" />
            <h3 className="text-headline-md text-on-surface">Top tip</h3>
          </div>
          {recos.isLoading ? (
            <Skeleton className="h-20" />
          ) : topReco ? (
            <>
              <p className="text-body-md text-on-surface">{topReco.message}</p>
              <span className="inline-block w-fit rounded-full bg-surface-container px-3 py-1 text-label-md uppercase text-on-surface-variant">
                {topReco.priority} priority · {topReco.type}
              </span>
            </>
          ) : (
            <p className="text-body-md text-on-surface-variant">Log a few days to see personalized tips.</p>
          )}
          {summary.data && (
            <div className="mt-auto rounded-lg bg-surface-container-low p-3">
              <p className="text-label-md uppercase text-on-surface-variant">Active days</p>
              <p className="text-headline-md text-on-surface">
                {summary.data.active_days}<span className="text-body-md text-on-surface-variant"> / {summary.data.total_days}</span>
              </p>
            </div>
          )}
        </Card>
      </div>
    </div>
  )
}

function MetricCard({
  icon,
  label,
  value,
  target,
  unit,
  formatValue,
}: {
  icon: React.ReactNode
  label: string
  value: number | null
  target: number
  unit: string
  formatValue: (v: number) => string
}) {
  const pct = value === null ? 0 : Math.min(100, (value / target) * 100)
  return (
    <Card className="flex items-center gap-md">
      <ProgressRing value={pct} size={72} stroke={8}>
        <div className="text-on-surface-variant">{icon}</div>
      </ProgressRing>
      <div>
        <p className="text-label-lg uppercase text-on-surface-variant">{label}</p>
        <p className="text-headline-md text-on-surface">
          {value === null ? '—' : formatValue(value)}{unit}
        </p>
        <p className="text-body-sm text-on-surface-variant">/ {formatValue(target)}{unit}</p>
      </div>
    </Card>
  )
}
