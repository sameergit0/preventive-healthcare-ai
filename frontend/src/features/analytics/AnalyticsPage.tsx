import { useState } from 'react'
import { format, subDays } from 'date-fns'
import { Footprints, Moon, Droplet, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { LineChart, Line, ResponsiveContainer, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts'
import { Card } from '@/components/ui/Card'
import { Chip } from '@/components/ui/Chip'
import { ProgressRing } from '@/components/ui/ProgressRing'
import { Skeleton } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'
import { useInsights, useRecommendations, useScoreHistory, useSummary, useTrends } from './api'
import type { MetricSummary, MetricTrend, Severity, MetricType } from '@/types/api'
import { cn, formatNumber } from '@/lib/utils'

const presets: { label: string; days: number }[] = [
  { label: '7d', days: 7 },
  { label: '30d', days: 30 },
  { label: '90d', days: 90 },
]

const severityClass: Record<Severity, string> = {
  good: 'bg-tertiary-fixed text-on-tertiary-fixed-variant',
  warning: 'bg-secondary-fixed text-on-secondary-fixed-variant',
  critical: 'bg-error-container text-on-error-container',
}

const priorityClass: Record<string, string> = {
  high: 'bg-error-container text-on-error-container',
  medium: 'bg-secondary-fixed text-on-secondary-fixed-variant',
  low: 'bg-tertiary-fixed text-on-tertiary-fixed-variant',
}

const metricIcon: Record<MetricType, React.ReactNode> = {
  steps: <Footprints className="h-5 w-5" />,
  sleep: <Moon className="h-5 w-5" />,
  water: <Droplet className="h-5 w-5" />,
}

export function AnalyticsPage() {
  const [days, setDays] = useState(30)
  const end = format(new Date(), 'yyyy-MM-dd')
  const start = format(subDays(new Date(), days - 1), 'yyyy-MM-dd')
  const [includeEmpty, setIncludeEmpty] = useState(true)

  const summary = useSummary(start, end)
  const insights = useInsights(start, end)
  const trends = useTrends(start, end)
  const recos = useRecommendations(start, end)
  const scores = useScoreHistory(start, end, includeEmpty)

  const noData = summary.data && summary.data.active_days === 0

  return (
    <div className="flex flex-col gap-md">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-headline-xl text-on-surface">Analytics</h1>
          <p className="mt-1 text-body-md text-on-surface-variant">{format(new Date(start), 'MMM d')} – {format(new Date(end), 'MMM d, yyyy')}</p>
        </div>
        <div className="flex gap-2">
          {presets.map((p) => (
            <Chip key={p.label} selected={days === p.days} onClick={() => setDays(p.days)}>{p.label}</Chip>
          ))}
        </div>
      </div>

      {noData && (
        <EmptyState title="No data in this range" description="Log a few days to unlock insights, trends and recommendations." />
      )}

      {/* Hero score */}
      <Card className="flex flex-col items-center gap-md sm:flex-row sm:justify-between">
        <div className="flex items-center gap-md">
          {insights.isLoading ? (
            <Skeleton className="h-32 w-32 rounded-full" />
          ) : (
            <ProgressRing value={insights.data?.overall_score ?? 0} size={128} stroke={12} fillClassName="text-primary">
              <div className="text-center">
                <p className="text-headline-lg text-on-surface">{insights.data?.overall_score ?? 0}</p>
                <p className="text-label-md text-on-surface-variant">overall</p>
              </div>
            </ProgressRing>
          )}
          <div>
            <p className="text-label-lg uppercase text-on-surface-variant">Health score</p>
            <p className="text-body-md text-on-surface">Weighted average across steps, sleep and water.</p>
          </div>
        </div>
        {summary.data && (
          <div className="grid grid-cols-2 gap-md text-center sm:grid-cols-2">
            <div>
              <p className="text-headline-md text-on-surface">{summary.data.active_days}</p>
              <p className="text-label-md uppercase text-on-surface-variant">Active days</p>
            </div>
            <div>
              <p className="text-headline-md text-on-surface">{summary.data.total_days}</p>
              <p className="text-label-md uppercase text-on-surface-variant">Total days</p>
            </div>
          </div>
        )}
      </Card>

      {/* Score history */}
      <Card>
        <div className="flex items-center justify-between">
          <h3 className="text-headline-md text-on-surface">Daily score</h3>
          <label className="flex items-center gap-2 text-body-sm text-on-surface-variant">
            <input type="checkbox" checked={includeEmpty} onChange={(e) => setIncludeEmpty(e.target.checked)} className="h-4 w-4 accent-primary" />
            Include empty days
          </label>
        </div>
        <div className="mt-3 h-64">
          {scores.isLoading ? (
            <Skeleton className="h-full" />
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={scores.data?.scores ?? []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#c3c6d7" />
                <XAxis dataKey="date" tickFormatter={(d) => format(new Date(d), 'MMM d')} stroke="#737686" fontSize={12} />
                <YAxis domain={[0, 100]} stroke="#737686" fontSize={12} />
                <Tooltip />
                <Line type="monotone" dataKey="score" stroke="#004ac6" strokeWidth={3} dot={{ r: 3 }} connectNulls />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      </Card>

      {/* Summary cards */}
      <div className="grid grid-cols-1 gap-md md:grid-cols-3">
        {summary.isLoading
          ? Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-48" />)
          : summary.data && (
              <>
                <SummaryCard type="steps" data={summary.data.steps} valueFmt={(v) => formatNumber(v)} unit="" />
                <SummaryCard type="sleep" data={summary.data.sleep} valueFmt={(v) => v.toFixed(1)} unit="h" />
                <SummaryCard type="water" data={summary.data.water} valueFmt={(v) => v.toFixed(1)} unit="L" />
              </>
            )}
      </div>

      {/* Trends */}
      <div className="grid grid-cols-1 gap-md md:grid-cols-3">
        {trends.isLoading
          ? Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-32" />)
          : trends.data && (
              <>
                <TrendCard type="steps" data={trends.data.steps} fmt={(v) => formatNumber(v)} unit="" />
                <TrendCard type="sleep" data={trends.data.sleep} fmt={(v) => v.toFixed(1)} unit="h" />
                <TrendCard type="water" data={trends.data.water} fmt={(v) => v.toFixed(1)} unit="L" />
              </>
            )}
      </div>

      {/* Insights */}
      <Card>
        <h3 className="text-headline-md text-on-surface">Insights</h3>
        <div className="mt-3 flex flex-col gap-2">
          {insights.isLoading
            ? Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-14" />)
            : insights.data?.insights.map((i) => (
                <div key={i.type} className="flex items-start gap-3 rounded-lg bg-surface-container-low p-3">
                  <span className={cn('inline-flex items-center gap-1 rounded-full px-2 py-1 text-label-md uppercase', severityClass[i.severity])}>
                    {metricIcon[i.type]} {i.severity}
                  </span>
                  <p className="text-body-md text-on-surface">{i.message}</p>
                </div>
              ))}
        </div>
      </Card>

      {/* Recommendations */}
      <Card>
        <h3 className="text-headline-md text-on-surface">Recommendations</h3>
        <div className="mt-3 flex flex-col gap-2">
          {recos.isLoading
            ? Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-14" />)
            : recos.data?.recommendations.map((r) => (
                <div key={r.type} className="flex items-start gap-3 rounded-lg bg-surface-container-low p-3">
                  <span className={cn('inline-flex items-center gap-1 rounded-full px-2 py-1 text-label-md uppercase', priorityClass[r.priority])}>
                    {metricIcon[r.type]} {r.priority}
                  </span>
                  <p className="text-body-md text-on-surface">{r.message}</p>
                </div>
              ))}
        </div>
      </Card>
    </div>
  )
}

function SummaryCard({ type, data, valueFmt, unit }: { type: MetricType; data: MetricSummary; valueFmt: (v: number) => string; unit: string }) {
  return (
    <Card className="flex flex-col gap-3">
      <div className="flex items-center gap-2">
        <span className="text-on-surface-variant">{metricIcon[type]}</span>
        <h4 className="text-headline-md capitalize text-on-surface">{type}</h4>
      </div>
      <div className="flex items-end justify-between">
        <div>
          <p className="text-label-md uppercase text-on-surface-variant">Average</p>
          <p className="text-headline-lg text-on-surface">{data.average === null ? '—' : valueFmt(data.average)}<span className="text-body-md text-on-surface-variant">{unit}</span></p>
        </div>
        {data.achievement_rate !== null && (
          <ProgressRing value={data.achievement_rate} size={56} stroke={6}>
            <span className="text-label-lg text-on-surface">{Math.round(data.achievement_rate)}%</span>
          </ProgressRing>
        )}
      </div>
      <div className="grid grid-cols-3 gap-2 text-center">
        <Stat label="Min" value={data.min === null ? '—' : valueFmt(data.min) + unit} />
        <Stat label="Max" value={data.max === null ? '—' : valueFmt(data.max) + unit} />
        <Stat label="Days" value={String(data.days_recorded)} />
      </div>
    </Card>
  )
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-surface-container-low p-2">
      <p className="text-label-md uppercase text-on-surface-variant">{label}</p>
      <p className="text-body-md font-semibold text-on-surface">{value}</p>
    </div>
  )
}

function TrendCard({ type, data, fmt, unit }: { type: MetricType; data: MetricTrend; fmt: (v: number) => string; unit: string }) {
  const change = data.change_percent
  const Trend = change === null || change === 0 ? Minus : change > 0 ? TrendingUp : TrendingDown
  const trendColor = change === null || change === 0 ? 'text-on-surface-variant' : change > 0 ? 'text-tertiary' : 'text-error'
  return (
    <Card className="flex flex-col gap-2">
      <div className="flex items-center gap-2">
        <span className="text-on-surface-variant">{metricIcon[type]}</span>
        <h4 className="text-headline-md capitalize text-on-surface">{type}</h4>
      </div>
      <div className="flex items-end justify-between">
        <div>
          <p className="text-label-md uppercase text-on-surface-variant">Current avg</p>
          <p className="text-headline-md text-on-surface">{data.current_avg === null ? '—' : fmt(data.current_avg) + unit}</p>
          <p className="text-body-sm text-on-surface-variant">prev {data.previous_avg === null ? '—' : fmt(data.previous_avg) + unit}</p>
        </div>
        <div className={cn('flex items-center gap-1 text-body-md font-semibold', trendColor)}>
          <Trend className="h-5 w-5" />
          {change === null ? '—' : `${change > 0 ? '+' : ''}${change.toFixed(1)}%`}
        </div>
      </div>
    </Card>
  )
}
