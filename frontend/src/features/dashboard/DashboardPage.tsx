import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { format, subDays } from 'date-fns'
import { Footprints, Moon, Droplet, ArrowRight, Sparkles, Plus, UtensilsCrossed, Clock, Candy, Apple } from 'lucide-react'
import { LineChart, Line, ResponsiveContainer, XAxis, YAxis, Tooltip } from 'recharts'
import { Card } from '@/components/ui/Card'
import { Modal } from '@/components/ui/Modal'
import { ProgressRing } from '@/components/ui/ProgressRing'
import { Skeleton } from '@/components/ui/Skeleton'
import { useProfile } from '@/features/profile/api'
import { useTodayLog, useUpsertTodayLog } from '@/features/logs/api'
import { LogEntryForm, type LogField } from '@/features/logs/LogEntryForm'
import { useRecommendations, useScoreHistory, useSummary } from '@/features/analytics/api'
import { formatNumber, cn } from '@/lib/utils'
import { type Profile } from '@/types/api'

const TARGETS = { steps: 10000, sleep: 7.5, water: 2.7, activity: 30 }

export function DashboardPage() {
  const [quickLog, setQuickLog] = useState<LogField | null>(null)
  const { data: profile } = useProfile()
  const today = useTodayLog()
  const upsert = useUpsertTodayLog()
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
          Full log <ArrowRight className="h-4 w-4" />
        </Link>
      </div>

      {/* Quick Log Buttons */}
      <div className="flex flex-wrap gap-2">
        <QuickLogButton
          icon={<Footprints className="h-4 w-4" />}
          label="Steps"
          onClick={() => setQuickLog('steps')}
          className="bg-secondary-fixed text-on-secondary-fixed-variant"
        />
        <QuickLogButton
          icon={<Moon className="h-4 w-4" />}
          label="Sleep"
          onClick={() => setQuickLog('sleep')}
          className="bg-primary-fixed text-on-primary-fixed-variant"
        />
        <QuickLogButton
          icon={<Droplet className="h-4 w-4" />}
          label="Water"
          onClick={() => setQuickLog('water')}
          className="bg-tertiary-fixed text-on-tertiary-fixed-variant"
        />
        <QuickLogButton
          icon={<UtensilsCrossed className="h-4 w-4" />}
          label="Food"
          onClick={() => setQuickLog('food')}
          className="bg-surface-container-high text-on-surface"
        />
        <QuickLogButton
          icon={<Clock className="h-4 w-4" />}
          label="Activity"
          onClick={() => setQuickLog('activity')}
          className="bg-secondary-fixed-dim text-on-secondary-fixed"
        />
        <QuickLogButton
          icon={<Candy className="h-4 w-4" />}
          label="Sugar"
          onClick={() => setQuickLog('sugar')}
          className="bg-error-container text-on-error-container"
        />
        <QuickLogButton
          icon={<Apple className="h-4 w-4" />}
          label="Fruits"
          onClick={() => setQuickLog('fruits')}
          className="bg-tertiary-container text-on-tertiary-container"
        />
      </div>

      {/* Top row */}
      <div className="grid grid-cols-1 gap-md sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-6">
        <Card className="flex flex-col items-center gap-2 p-3 text-center">
          <ProgressRing value={todayScore ?? 0} size={64} stroke={6} fillClassName="text-primary">
            <div className="text-center">
              <p className="text-title-lg font-bold text-on-surface">{todayScore ?? '—'}</p>
            </div>
          </ProgressRing>
          <div className="min-w-0">
            <p className="text-label-sm uppercase tracking-wider text-on-surface-variant">Score</p>
            <p className="text-body-xs text-on-surface-variant">Today's wellness</p>
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
        <MetricCard
          icon={<Clock className="h-5 w-5" />}
          label="Activity"
          value={log?.activity_minutes ?? null}
          target={TARGETS.activity}
          unit="m"
          formatValue={(v) => v.toFixed(0)}
        />
        <HealthStatsCard profile={profile?.profile} />
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

      <Modal
        open={!!quickLog}
        onClose={() => setQuickLog(null)}
        title={quickLog ? `Log ${quickLog.charAt(0).toUpperCase() + quickLog.slice(1)}` : ''}
        className="max-w-2xl"
      >
        {quickLog && (
          <LogEntryForm
            initial={log}
            fields={[quickLog]}
            onSubmit={async (body) => {
              await upsert.mutateAsync(body)
              setQuickLog(null)
            }}
            submitting={upsert.isPending}
            submitLabel={`Save ${quickLog}`}
          />
        )}
      </Modal>
    </div>
  )
}

function QuickLogButton({
  icon,
  label,
  onClick,
  className,
}: {
  icon: React.ReactNode
  label: string
  onClick: () => void
  className?: string
}) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'inline-flex items-center gap-2 rounded-full px-4 py-2 text-label-lg transition-transform hover:scale-105 active:scale-95',
        className
      )}
    >
      <Plus className="h-4 w-4" />
      {icon}
      <span>{label}</span>
    </button>
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
    <Card className="flex flex-col items-center gap-2 p-3 text-center min-w-0">
      <ProgressRing value={pct} size={56} stroke={6}>
        <div className="text-on-surface-variant">{icon}</div>
      </ProgressRing>
      <div className="min-w-0">
        <p className="text-label-sm uppercase tracking-wider text-on-surface-variant">{label}</p>
        <p className="text-title-md font-bold text-on-surface">
          {value === null ? '—' : formatValue(value)}{unit}
        </p>
        <p className="text-body-xs text-on-surface-variant">/ {formatValue(target)}{unit}</p>
      </div>
    </Card>
  )
}

function HealthStatsCard({ profile }: { profile: Profile }) {
  if (!profile?.bmi) return null
  return (
    <Card className="flex flex-col items-center justify-center gap-2 p-3 text-center min-w-0">
      <p className="text-label-sm uppercase tracking-wider text-on-surface-variant">Profile</p>
      <div className="flex items-baseline gap-1">
        <span className="text-title-lg font-bold text-on-surface">{profile.bmi}</span>
        <span className="text-body-xs text-on-surface-variant uppercase">BMI</span>
      </div>
      <div className={cn(
        "text-label-xs font-bold uppercase px-2 py-0.5 rounded-full bg-surface-container-high",
        profile.bmi_category === 'Normal' ? "text-tertiary" : "text-error"
      )}>
        {profile.bmi_category}
      </div>
    </Card>
  )
}
