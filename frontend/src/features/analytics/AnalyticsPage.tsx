import { useState } from 'react'
import { format, subDays } from 'date-fns'
import {
  Footprints, Moon, Droplet, Calendar, Clock, Timer, Apple, Candy,
  TrendingUp, TrendingDown, Minus, AlertTriangle, ShieldCheck,
} from 'lucide-react'
import {
  LineChart, Line, ResponsiveContainer, XAxis, YAxis, Tooltip, CartesianGrid,
  BarChart, Bar, Cell,
} from 'recharts'
import { Card } from '@/components/ui/Card'
import { Chip } from '@/components/ui/Chip'
import { ProgressRing } from '@/components/ui/ProgressRing'
import { Skeleton } from '@/components/ui/Skeleton'
import { useInsights, useRecommendations, useSummary, useTrends } from './api'
import type { MetricSummary, MetricKey } from '@/types/api'
import { cn, formatNumber } from '@/lib/utils'

const presets: { label: string; days: number | 'custom' }[] = [
  { label: '7d', days: 7 },
  { label: '30d', days: 30 },
  { label: '90d', days: 90 },
  { label: 'Custom', days: 'custom' },
]

const priorityClass: Record<string, string> = {
  high: 'bg-error-container text-on-error-container',
  medium: 'bg-secondary-fixed text-on-secondary-fixed-variant',
  low: 'bg-tertiary-fixed text-on-tertiary-fixed-variant',
}

const trendBadge: Record<string, { icon: typeof TrendingUp; color: string }> = {
  improving: { icon: TrendingUp, color: 'text-tertiary' },
  declining: { icon: TrendingDown, color: 'text-error' },
  stable: { icon: Minus, color: 'text-on-surface-variant' },
}

const metricIcon: Record<MetricKey, React.ReactNode> = {
  steps: <Footprints className="h-5 w-5" />,
  sleep: <Moon className="h-5 w-5" />,
  water: <Droplet className="h-5 w-5" />,
  activity: <Clock className="h-5 w-5" />,
  sedentary: <Timer className="h-5 w-5" />,
  sugar: <Candy className="h-5 w-5" />,
  fruits: <Apple className="h-5 w-5" />,
}

const metricUnit: Record<MetricKey, string> = {
  steps: '', sleep: 'h', water: 'L', activity: 'm',
  sedentary: 'm', sugar: 'g', fruits: '',
}

const metricFmt: Record<MetricKey, (v: number) => string> = {
  steps: (v) => formatNumber(v),
  sleep: (v) => v.toFixed(1),
  water: (v) => v.toFixed(1),
  activity: (v) => v.toFixed(0),
  sedentary: (v) => v.toFixed(0),
  sugar: (v) => v.toFixed(1),
  fruits: (v) => v.toFixed(0),
}

export function AnalyticsPage() {
  const [days, setDays] = useState<number | 'custom'>(30)
  const [showPerformance, setShowPerformance] = useState(false)
  const [customStart, setCustomStart] = useState(format(subDays(new Date(), 30), 'yyyy-MM-dd'))
  const [customEnd, setCustomEnd] = useState(format(new Date(), 'yyyy-MM-dd'))

  const end = days === 'custom' ? customEnd : format(new Date(), 'yyyy-MM-dd')
  const start = days === 'custom' ? customStart : format(subDays(new Date(), (days as number) - 1), 'yyyy-MM-dd')

  const summary = useSummary(start, end)
  const insights = useInsights()
  const trends = useTrends(start, end)
  const recos = useRecommendations()

  return (
    <div className="flex flex-col gap-md">
      {/* Header */}
      <div>
        <h1 className="text-headline-xl text-on-surface">Analytics</h1>
      </div>

      {/* 7-Day Performance Trigger */}
      <div
        onClick={() => setShowPerformance(!showPerformance)}
        className="cursor-pointer inline-flex items-center gap-3 self-start rounded-2xl bg-secondary-container px-5 py-3 text-on-secondary-container shadow-sm transition-all hover:bg-secondary-container/80 hover:shadow-md active:scale-95"
      >
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-secondary text-on-secondary">
          <TrendingUp className="h-5 w-5" />
        </div>
        <div>
          <p className="text-label-lg font-bold">Check your 7-day performance</p>
          <p className="text-label-small opacity-80">Click here to view your weekly health assessment</p>
        </div>
      </div>

      {showPerformance && (
        <div className="flex flex-col gap-md animate-in fade-in slide-in-from-top-4 duration-300">
          {/* Hero: Health Score + Risk */}
          <Card className="flex flex-col items-center gap-md sm:flex-row sm:justify-between !bg-surface-container-low border-none shadow-none">
            <div className="flex items-center gap-md">
              {insights.isLoading ? (
                <Skeleton className="h-32 w-32 rounded-full" />
              ) : (
                <ProgressRing value={insights.data?.health_score ?? 0} size={128} stroke={12} fillClassName="text-error" trackClassName="text-error-container/40">
                  <div className="text-center">
                    <p className="text-headline-lg text-on-surface">{insights.data?.health_score ?? 0}</p>
                    <p className="text-label-md text-on-surface-variant">score</p>
                  </div>
                </ProgressRing>
              )}
              <div>
                <h2 className="text-headline-md font-bold text-on-surface">Weekly Assessment</h2>
                <p className="text-body-sm text-on-surface-variant">
                  Your 7-day weighted average across behavior, lifestyle, and medical context.
                </p>
                {insights.data && (
                  <div className="mt-3 flex items-center gap-2">
                    {insights.data.risk_level === 'Low' ? (
                      <ShieldCheck className="h-5 w-5 text-tertiary" />
                    ) : (
                      <AlertTriangle className="h-5 w-5 text-error" />
                    )}
                    <span className={cn(
                      'rounded-full px-3 py-1 text-label-md font-bold uppercase tracking-wider',
                      insights.data.risk_level === 'Low' ? 'bg-tertiary-fixed text-on-tertiary-fixed-variant'
                        : insights.data.risk_level === 'Moderate' ? 'bg-secondary-fixed text-on-secondary-fixed-variant'
                          : 'bg-error-container text-on-error-container'
                    )}>
                      {insights.data.risk_level} risk level
                    </span>
                  </div>
                )}
              </div>
            </div>
            {insights.data && (
              <div className="max-w-xs rounded-xl bg-surface-container p-4 border border-outline-variant">
                <p className="text-body-md text-on-surface font-medium italic">"{insights.data.summary_message}"</p>
              </div>
            )}
          </Card>

          {/* Insights List */}
          <Card className="border-none bg-surface-container-low shadow-none">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="h-5 w-5 text-primary" />
              <h3 className="text-headline-md text-on-surface">Health Insights</h3>
            </div>
            <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
              {insights.isLoading
                ? Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-20" />)
                : insights.data?.insights.length ? (
                  insights.data.insights.map((insight, idx) => {
                    const badge = trendBadge[insight.trend ?? 'stable'] ?? trendBadge.stable
                    const TrendIcon = badge.icon
                    return (
                      <div key={idx} className="flex items-start gap-4 rounded-xl bg-surface-container p-4 transition-colors hover:bg-surface-container-high">
                        <div className="flex flex-col items-center gap-2">
                          <span className={cn('inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-label-xs font-bold uppercase', priorityClass[insight.priority] ?? priorityClass.low)}>
                            {insight.priority}
                          </span>
                          <div className={cn('flex items-center gap-1 text-label-xs font-semibold', badge.color)}>
                            <TrendIcon className="h-3 w-3" />
                            <span className="capitalize">{insight.trend ?? 'stable'}</span>
                          </div>
                        </div>
                        <div className="min-w-0">
                          <p className="text-label-sm uppercase font-bold tracking-wider text-on-surface-variant mb-1">{insight.category}</p>
                          <p className="text-body-md text-on-surface leading-relaxed">{insight.message}</p>
                        </div>
                      </div>
                    )
                  })
                ) : (
                  <p className="text-body-md text-on-surface-variant italic py-4 text-center col-span-full">Log more data to see detailed insights.</p>
                )}
            </div>
          </Card>
        </div>
      )}

      {/* Filters + Date Range */}
      <div className="flex flex-wrap items-end justify-between gap-3 border-t border-outline-variant pt-4">
        <div>
          <p className="text-body-md text-on-surface-variant">
            {format(new Date(start), 'MMM d')} – {format(new Date(end), 'MMM d, yyyy')}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {days === 'custom' && (
            <div className="flex items-center gap-2 mr-2">
              <div className="flex items-center gap-1.5 rounded-lg bg-surface-container-low px-3 py-2">
                <Calendar className="h-4 w-4 text-on-surface-variant" />
                <input type="date" value={customStart} onChange={(e) => setCustomStart(e.target.value)} className="bg-transparent text-body-sm outline-none" />
              </div>
              <span className="text-on-surface-variant">→</span>
              <div className="flex items-center gap-1.5 rounded-lg bg-surface-container-low px-3 py-2">
                <Calendar className="h-4 w-4 text-on-surface-variant" />
                <input type="date" value={customEnd} onChange={(e) => setCustomEnd(e.target.value)} className="bg-transparent text-body-sm outline-none" />
              </div>
            </div>
          )}
          <div className="flex gap-2">
            {presets.map((p) => (
              <Chip key={p.label} selected={days === p.days} onClick={() => setDays(p.days)}>{p.label}</Chip>
            ))}
          </div>
        </div>
      </div>

      {/* Summary Metric Cards — top row */}
      <div className="grid grid-cols-1 gap-md md:grid-cols-2 lg:grid-cols-4">
        {summary.isLoading
          ? Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-48" />)
          : summary.data && (
            <>
              <SummaryCard type="steps" data={summary.data.steps} />
              <SummaryCard type="sleep" data={summary.data.sleep} />
              <SummaryCard type="water" data={summary.data.water} />
              <SummaryCard type="activity" data={summary.data.activity} />
            </>
          )}
      </div>

      {/* Summary Metric Cards — bottom row */}
      <div className="grid grid-cols-1 gap-md md:grid-cols-3">
        {summary.isLoading
          ? Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-48" />)
          : summary.data && (
            <>
              <SummaryCard type="sedentary" data={summary.data.sedentary} />
              <SummaryCard type="sugar" data={summary.data.sugar} />
              <SummaryCard type="fruits" data={summary.data.fruits} />
            </>
          )}
      </div>

      {/* Coach Tasks */}
      <Card className="h-full">
        <div className="flex items-center gap-2 mb-4">
          <ShieldCheck className="h-5 w-5 text-tertiary" />
          <h3 className="text-headline-md text-on-surface">Coach Tasks</h3>
        </div>
        <div className="flex flex-col gap-3">
          {recos.isLoading
            ? Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-24" />)
            : recos.data?.recommendations.length ? (
              recos.data.recommendations.map((r, idx) => (
                <div key={idx} className="flex items-start gap-4 rounded-xl bg-surface-container-low p-4 border border-transparent transition-all hover:border-outline-variant hover:bg-surface-container">
                  <span className={cn('shrink-0 inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-label-xs font-bold uppercase', priorityClass[r.priority] ?? priorityClass.low)}>
                    {r.priority}
                  </span>
                  <div className="min-w-0">
                    <p className="text-label-sm uppercase font-bold tracking-wider text-on-surface-variant mb-1">{r.category}</p>
                    <p className="text-body-md font-bold text-on-surface mb-1">{r.task}</p>
                    <p className="text-body-sm text-on-surface-variant leading-relaxed">{r.benefit}</p>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-body-md text-on-surface-variant italic py-4 text-center">No recommendations yet.</p>
            )}
        </div>
      </Card>
    </div>
  )
}

/* ─── Sub-components ──────────────────────────────────────────── */

function SummaryCard({ type, data }: { type: MetricKey; data: MetricSummary }) {
  const fmt = metricFmt[type]
  const unit = metricUnit[type]
  
  const chartData = [
    { name: 'Min', value: data.min },
    { name: 'Avg', value: data.avg },
    { name: 'Max', value: data.max },
  ]

  const themeColors: Record<MetricKey, string> = {
    steps: '#004ac1',
    sleep: '#4c5c92',
    water: '#0061a4',
    activity: '#ba1a1a',
    sedentary: '#737686',
    sugar: '#9c4146',
    fruits: '#006a6a',
  }

  return (
    <Card className="flex flex-col gap-4 overflow-hidden group hover:shadow-lg transition-all duration-300">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-surface-container-high text-primary group-hover:scale-110 transition-transform">
            {metricIcon[type]}
          </div>
          <h4 className="text-headline-sm capitalize text-on-surface">{type}</h4>
        </div>
        {data.days_recorded > 0 && (
          <div className="flex flex-col items-end">
            <span className="text-[10px] font-black uppercase tracking-widest text-on-surface-variant opacity-50">Achievement</span>
            <span className="text-body-md font-black text-primary">{Math.round(data.achievement_rate)}%</span>
          </div>
        )}
      </div>

      <div className="flex items-end justify-between gap-4">
        <div className="flex-1">
          <p className="text-label-xs font-black uppercase tracking-widest text-on-surface-variant opacity-60">Daily Average</p>
          <div className="flex items-baseline gap-1">
            <p className="text-display-xs font-black text-on-surface">
              {data.days_recorded === 0 ? '—' : fmt(data.avg)}
            </p>
            <span className="text-label-md font-bold text-on-surface-variant/70 uppercase">{unit}</span>
          </div>
        </div>
        
        <div className="h-16 w-32">
          {data.days_recorded > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 5, right: 5, left: 5, bottom: 0 }}>
                <Bar dataKey="value" radius={[2, 2, 0, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={themeColors[type]} 
                      fillOpacity={index === 0 ? 0.3 : index === 1 ? 0.6 : 1} 
                    />
                  ))}
                </Bar>
                <Tooltip 
                  cursor={{ fill: 'transparent' }}
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      return (
                        <div className="rounded-md bg-on-surface px-2 py-1 shadow-md">
                          <p className="text-[10px] font-black text-surface uppercase tracking-tighter">
                            {payload[0].payload.name}: {fmt(payload[0].value as number)}{unit}
                          </p>
                        </div>
                      )
                    }
                    return null
                  }}
                />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full w-full rounded-lg bg-surface-container-low flex items-center justify-center">
              <span className="text-[10px] uppercase font-bold opacity-30">No Data</span>
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-3 gap-2 border-t border-outline-variant/20 pt-4">
        <div className="flex flex-col">
          <span className="text-[9px] font-black uppercase text-on-surface-variant/50">Min</span>
          <span className="text-label-md font-bold text-on-surface">{data.days_recorded === 0 ? '—' : fmt(data.min)}</span>
        </div>
        <div className="flex flex-col text-center">
          <span className="text-[9px] font-black uppercase text-on-surface-variant/50">Max</span>
          <span className="text-label-md font-bold text-on-surface">{data.days_recorded === 0 ? '—' : fmt(data.max)}</span>
        </div>
        <div className="flex flex-col text-right">
          <span className="text-[9px] font-black uppercase text-on-surface-variant/50">Logged</span>
          <span className="text-label-md font-bold text-on-surface">{data.days_recorded}d</span>
        </div>
      </div>
    </Card>
  )
}
