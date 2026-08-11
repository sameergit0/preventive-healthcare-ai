import { useMemo, useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { format, subDays } from 'date-fns'
import { toast } from 'sonner'
import {
  Footprints, Moon, Droplet, ArrowRight, Sparkles, Plus,
  UtensilsCrossed, Clock, Candy, Apple,
  HeartPulse, Wine, Stethoscope, Activity,
  TrendingUp, TrendingDown, ShieldCheck,
  Cigarette, Brain, Monitor, Wind, Check, X
} from 'lucide-react'
import { LineChart, Line, ResponsiveContainer, XAxis, YAxis, Tooltip } from 'recharts'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Modal } from '@/components/ui/Modal'
import { ProgressRing } from '@/components/ui/ProgressRing'
import { Skeleton } from '@/components/ui/Skeleton'
import { Chip } from '@/components/ui/Chip'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { useProfile } from '@/features/profile/api'
import { useTodayLog, useUpsertTodayLog } from '@/features/logs/api'
import { LogEntryForm, type LogField } from '@/features/logs/LogEntryForm'
import { useRecommendations, useTrends, useStatus, useInsights } from '@/features/analytics/api'
import { 
  useDeleteLifestyle, useDeleteMedicalHistory, useGetLifestyle, useGetMedicalHistory,
  useCreateLifestyle, useUpdateLifestyle, useCreateMedicalHistory, useUpdateMedicalHistory 
} from '@/features/onboarding/api'
import { LifestyleModal } from '@/features/onboarding/LifestyleModal'
import { MedicalHistoryModal } from '@/features/onboarding/MedicalHistoryModal'
import { formatNumber, cn } from '@/lib/utils'
import { getErrorMessage } from '@/lib/api'
import { type Profile, TOBACCO_OPTIONS, ALCOHOL_OPTIONS, MEDICAL_CONDITIONS } from '@/types/api'

const TARGETS = { steps: 10000, sleep: 7.5, water: 2.7, activity: 30 }

export function DashboardPage() {
  const [quickLog, setQuickLog] = useState<LogField | null>(null)
  const [showBackground, setShowBackground] = useState(false)
  const [backgroundTab, setBackgroundTab] = useState<'lifestyle' | 'medical'>('lifestyle')

  const { data: profile } = useProfile()
  const today = useTodayLog()
  const upsert = useUpsertTodayLog()
  const end = format(new Date(), 'yyyy-MM-dd')
  const start7 = format(subDays(new Date(), 6), 'yyyy-MM-dd')

  const status = useStatus()
  const insights = useInsights()
  const trends = useTrends(start7, end)
  const recos = useRecommendations()
  const lifestyle = useGetLifestyle()
  const medicalHistory = useGetMedicalHistory()

  const log = today.data?.logs[0]

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
  const firstName = profile?.full_name.split(' ')[0] ?? ''

  // Determine which setup cards to show — wait until all queries finish loading
  const setupLoading = lifestyle.isLoading || medicalHistory.isLoading
  const hasLifestyle = lifestyle.data && !lifestyle.isError
  const hasMedical = medicalHistory.data && !medicalHistory.isError
  const showSetup = !setupLoading && (!hasLifestyle || !hasMedical)

  const deleteLifestyle = useDeleteLifestyle()
  const deleteMedical = useDeleteMedicalHistory()

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

      {/* Setup Cards — only shown when data is missing */}
      {showSetup && (
        <div className="grid grid-cols-1 gap-md sm:grid-cols-2 lg:grid-cols-3">
          {!hasLifestyle && (
            <Card className="flex flex-col gap-3 border-2 border-dashed border-outline-variant !bg-surface-container-low">
              <div className="flex items-center gap-2">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-secondary-container">
                  <Wine className="h-5 w-5 text-secondary-on-container" />
                </div>
                <div>
                  <p className="text-label-lg font-semibold text-on-surface">Lifestyle Profile</p>
                  <p className="text-body-sm text-on-surface-variant">Habits & wellness data</p>
                </div>
              </div>
              <p className="text-body-sm text-on-surface-variant">
                Add your lifestyle habits so we can provide better health insights and personalized recommendations.
              </p>
              <Button size="sm" variant="secondary" onClick={() => { setBackgroundTab('lifestyle'); setShowBackground(true); }} className="self-start">
                <Plus className="h-4 w-4" /> Complete Setup
              </Button>
            </Card>
          )}
          {!hasMedical && (
            <Card className="flex flex-col gap-3 border-2 border-dashed border-outline-variant !bg-surface-container-low">
              <div className="flex items-center gap-2">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-error-container">
                  <Stethoscope className="h-5 w-5 text-on-error-container" />
                </div>
                <div>
                  <p className="text-label-lg font-semibold text-on-surface">Medical History</p>
                  <p className="text-body-sm text-on-surface-variant">Conditions & diagnoses</p>
                </div>
              </div>
              <p className="text-body-sm text-on-surface-variant">
                Share any medical conditions to unlock risk-aware scoring and condition-specific coaching.
              </p>
              <Button size="sm" variant="secondary" onClick={() => { setBackgroundTab('medical'); setShowBackground(true); }} className="self-start">
                <Plus className="h-4 w-4" /> Add History
              </Button>
            </Card>
          )}

        </div>
      )}

      {/* Quick Log Buttons */}
      <div className="flex flex-wrap gap-2">
        <QuickLogButton icon={<Footprints className="h-4 w-4" />} label="Steps" onClick={() => setQuickLog('steps')} className="bg-secondary-fixed text-on-secondary-fixed-variant" />
        <QuickLogButton icon={<Moon className="h-4 w-4" />} label="Sleep" onClick={() => setQuickLog('sleep')} className="bg-primary-fixed text-on-primary-fixed-variant" />
        <QuickLogButton icon={<Droplet className="h-4 w-4" />} label="Water" onClick={() => setQuickLog('water')} className="bg-tertiary-fixed text-on-tertiary-fixed-variant" />
        <QuickLogButton icon={<UtensilsCrossed className="h-4 w-4" />} label="Food" onClick={() => setQuickLog('food')} className="bg-surface-container-high text-on-surface" />
        <QuickLogButton icon={<Clock className="h-4 w-4" />} label="Activity" onClick={() => setQuickLog('activity')} className="bg-secondary-fixed-dim text-on-secondary-fixed" />
        <QuickLogButton icon={<Candy className="h-4 w-4" />} label="Sugar" onClick={() => setQuickLog('sugar')} className="bg-error-container text-on-error-container" />
        <QuickLogButton icon={<Apple className="h-4 w-4" />} label="Fruits" onClick={() => setQuickLog('fruits')} className="bg-tertiary-container text-on-tertiary-container" />
      </div>

      {/* Top row: Score + Metrics */}
      {/* Top row: Assessment + Profile */}
      <div className="grid grid-cols-1 gap-md lg:grid-cols-4">
        {/* Health Status Card — Premium Hero View */}
        <Card className="col-span-1 overflow-hidden lg:col-span-3 !p-0 border-none shadow-lg shadow-primary/5">
          <div className="flex flex-col md:flex-row h-full">
            {/* Hero Section */}
            <div className="relative flex flex-col items-center justify-center gap-4 bg-surface-container-low p-6 md:w-1/3 border-r border-outline-variant/20">
              <div className="absolute top-5 left-5 text-headline-sm font-bold text-on-surface uppercase tracking-tight">Overall</div>
              <div className="relative flex h-28 w-28 items-center justify-center">
                <ProgressRing 
                  value={status.data?.health_score ?? 0} 
                  size={112} 
                  stroke={10} 
                  fillClassName="text-error"
                  trackClassName="text-error-container/40"
                >
                  <div className="flex flex-col items-center">
                    <span className="text-display-sm font-black tracking-tighter text-on-surface">{status.data?.health_score ?? '—'}</span>
                    <span className="text-label-xs font-bold text-on-surface-variant opacity-70">SCORE</span>
                  </div>
                </ProgressRing>
              </div>
              <div className="flex flex-col items-center">
                <div className="flex items-center gap-1.5 rounded-full bg-primary-container/40 px-3 py-1 border border-primary/10">
                  <ShieldCheck className="h-4 w-4 text-primary" />
                  <span className="text-label-sm font-bold uppercase tracking-wider text-on-primary-container">{status.data?.risk_level ?? '—'} Risk</span>
                </div>
              </div>
            </div>

            {/* Details Section */}
            <div className="flex flex-1 flex-col justify-between p-6 bg-surface">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-headline-sm font-bold text-on-surface">Health Assessment</h3>
                  <p className="text-body-sm text-on-surface-variant">Real-time analysis of your wellness data.</p>
                </div>
                <div className="flex items-center gap-2 rounded-full bg-secondary-container/30 px-3 py-1">
                  <span className="h-2 w-2 animate-pulse rounded-full bg-primary" />
                  <span className="text-label-xs font-bold text-on-secondary-container uppercase">Live Data</span>
                </div>
              </div>

              <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div className="flex flex-col gap-1 rounded-2xl bg-surface-container-low p-4 border border-outline-variant/30">
                  <div className="flex items-center justify-between">
                    <p className="text-label-sm font-semibold uppercase tracking-wider text-on-surface-variant">7-Day Average</p>
                    {status.data && insights.data && (
                      status.data.health_score > insights.data.health_score ? 
                      <TrendingUp className="h-4 w-4 text-tertiary" /> : 
                      <TrendingDown className="h-4 w-4 text-error" />
                    )}
                  </div>
                  <div className="flex items-end gap-2">
                    <span className="text-headline-md font-bold text-on-surface">{insights.data?.health_score ?? '—'}</span>
                    <span className="mb-1 text-body-sm text-on-surface-variant">/ 100</span>
                  </div>
                </div>

                <div className="flex flex-col gap-1 rounded-2xl bg-surface-container-low p-4 border border-outline-variant/30">
                  <p className="text-label-sm font-semibold uppercase tracking-wider text-on-surface-variant">Overall Risk</p>
                  <div className="flex items-center gap-2 mt-1">
                    <div className={cn(
                      "h-3 w-3 rounded-full",
                      (status.data?.health_score ?? 0) >= 80 ? "bg-tertiary" : (status.data?.health_score ?? 0) >= 50 ? "bg-primary" : "bg-error"
                    )} />
                    <span className="text-body-md font-bold text-on-surface">
                      Your health is {status.data && insights.data && status.data.health_score > insights.data.health_score ? 'improving' : 'stable'}
                    </span>
                  </div>
                  <p className="text-body-xs text-on-surface-variant cursor-default">
                    Compared to your weekly baseline.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </Card>
        <HealthStatsCard profile={profile} />
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 gap-md lg:grid-cols-4">
        <MetricCard 
          icon={<Footprints className="h-4 w-4" />} 
          label="Steps" 
          value={log?.steps ?? null} 
          target={TARGETS.steps} 
          unit="" 
          formatValue={(v) => formatNumber(v)} 
          theme="secondary"
        />
        <MetricCard 
          icon={<Moon className="h-4 w-4" />} 
          label="Sleep" 
          value={log?.sleep_hours ?? null} 
          target={TARGETS.sleep} 
          unit="h" 
          formatValue={(v) => v.toFixed(1)} 
          theme="primary"
        />
        <MetricCard 
          icon={<Droplet className="h-4 w-4" />} 
          label="Water" 
          value={log?.water_intake ?? null} 
          target={TARGETS.water} 
          unit="L" 
          formatValue={(v) => v.toFixed(1)} 
          theme="tertiary"
        />
        <MetricCard 
          icon={<Clock className="h-4 w-4" />} 
          label="Activity" 
          value={log?.activity_minutes ?? null} 
          target={TARGETS.activity} 
          unit="m" 
          formatValue={(v) => v.toFixed(0)} 
          theme="error"
        />
      </div>

      {/* Chart + Insights + Background */}
      <div className="grid grid-cols-1 gap-md lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <div className="flex items-center justify-between">
            <h3 className="text-headline-md text-on-surface">7-day score</h3>
            <Link to="/analytics" className="text-body-sm text-primary hover:underline">View analytics</Link>
          </div>
          <div className="mt-3 h-48">
            {trends.isLoading ? (
              <Skeleton className="h-full" />
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trends.data?.data ?? []}>
                  <XAxis dataKey="log_date" tickFormatter={(d) => format(new Date(d), 'EEE')} stroke="#737686" fontSize={12} />
                  <YAxis domain={[0, 100]} stroke="#737686" fontSize={12} />
                  <Tooltip labelFormatter={(d) => format(new Date(d as string), 'MMM d')} />
                  <Line type="monotone" dataKey="health_score" name="Score" stroke="#004ac6" strokeWidth={3} dot={{ r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
        </Card>

        <div className="flex flex-col gap-md lg:col-span-1">
          {/* Weekly Insights */}
          <Card className="flex flex-col gap-3 !p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-tertiary" />
                <h3 className="text-label-lg font-bold uppercase tracking-wider text-on-surface-variant">Weekly Insights</h3>
              </div>
              <Link to="/analytics" className="text-[10px] font-bold text-primary uppercase hover:underline">Full Report</Link>
            </div>
            
            <div className="flex flex-col gap-2">
              {insights.isLoading ? (
                Array.from({ length: 2 }).map((_, i) => <Skeleton key={i} className="h-8" />)
              ) : insights.data?.insights.length ? (
                insights.data.insights.slice(0, 2).map((insight, idx) => (
                  <div key={idx} className="flex gap-2 border-l-2 border-primary/20 pl-2">
                    <p className="line-clamp-2 text-body-xs text-on-surface">{insight.message}</p>
                  </div>
                ))
              ) : (
                <p className="text-body-xs text-on-surface-variant italic">Log more days for insights.</p>
              )}
            </div>
          </Card>

          {/* Compact Health Background */}
          <HealthBackgroundSection 
            lifestyle={lifestyle.data} 
            medical={medicalHistory.data}
            loading={lifestyle.isLoading || medicalHistory.isLoading}
            onEdit={() => { setBackgroundTab('lifestyle'); setShowBackground(true); }}
          />
        </div>
      </div>

      {recos.data?.recommendations[0] && (
        <Card className="!bg-tertiary-container/10 border-tertiary/20">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-tertiary/20">
              <Sparkles className="h-5 w-5 text-tertiary" />
            </div>
            <div>
              <p className="text-label-xs font-bold uppercase tracking-widest text-tertiary">Top Recommendation</p>
              <p className="text-body-md font-bold text-on-surface">{recos.data.recommendations[0].task}</p>
              <p className="text-body-xs text-on-surface-variant">{recos.data.recommendations[0].benefit}</p>
            </div>
          </div>
        </Card>
      )}

      {/* Quick Log Modal */}
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

      {/* Health Background Unified Modal */}
      <HealthBackgroundModal
        open={showBackground}
        onOpenChange={setShowBackground}
        initialTab={backgroundTab}
        lifestyleData={lifestyle.data}
        medicalData={medicalHistory.data}
        onComplete={() => {
          lifestyle.refetch()
          medicalHistory.refetch()
        }}
      />
    </div>
  )
}

/* ─── Sub-components ──────────────────────────────────────────── */

function QuickLogButton({ icon, label, onClick, className }: {
  icon: React.ReactNode; label: string; onClick: () => void; className?: string
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

function MetricCard({ icon, label, value, target, unit, formatValue, theme = 'primary' }: {
  icon: React.ReactNode; label: string; value: number | null; target: number; unit: string; formatValue: (v: number) => string;
  theme?: 'primary' | 'secondary' | 'tertiary' | 'error'
}) {
  const pct = value === null ? 0 : Math.min(100, (value / target) * 100)
  
  const themes = {
    primary: 'bg-primary-container/20 text-primary border-primary/10 hover:bg-primary-container/30 hover:border-primary/20',
    secondary: 'bg-secondary-container/20 text-secondary border-secondary/10 hover:bg-secondary-container/30 hover:border-secondary/20',
    tertiary: 'bg-tertiary-container/20 text-tertiary border-tertiary/10 hover:bg-tertiary-container/30 hover:border-tertiary/20',
    error: 'bg-error-container/15 text-error border-error/10 hover:bg-error-container/25 hover:border-error/20',
  }

  return (
    <Card className={cn(
      "flex flex-col items-center gap-3 p-5 text-center min-w-0 transition-all duration-300 hover:-translate-y-1.5 hover:shadow-xl border-2",
      themes[theme]
    )}>
      <div className="relative">
        <ProgressRing 
          value={pct} 
          size={56} 
          stroke={6} 
          className="text-current"
          trackClassName="opacity-10"
        >
          <div className="scale-125 transition-transform group-hover:scale-110">{icon}</div>
        </ProgressRing>
      </div>
      
      <div className="flex flex-col items-center w-full">
        <p className="text-[10px] font-black uppercase tracking-[0.2em] opacity-50 mb-1">{label}</p>
        <div className="flex items-baseline gap-0.5">
          <span className="text-headline-md font-black tracking-tighter">
            {value === null ? '—' : formatValue(value)}
          </span>
          <span className="text-label-sm font-bold opacity-70 uppercase">{unit}</span>
        </div>
        
        <div className="mt-3 flex items-center gap-2 rounded-full bg-black/5 px-3 py-1 border border-black/20">
          <span className="text-[9px] font-black uppercase tracking-widest opacity-60 text-black">Goal</span>
          <div className="h-2 w-[1px] bg-black/10" />
          <span className="text-[10px] font-bold tracking-tight text-black">{formatValue(target)}{unit}</span>
        </div>
      </div>
    </Card>
  )
}

function HealthStatsCard({ profile }: { profile?: Profile }) {
  const [activeLabel, setActiveLabel] = useState<string | null>(null)
  
  if (!profile?.bmi) return null
  const bmiValue = profile.bmi
  const pct = Math.max(0, Math.min(100, ((bmiValue - 15) / (35 - 15)) * 100))
  
  return (
    <Card className="flex flex-col items-center justify-between gap-4 p-6 text-center min-w-0 bg-surface-container-low border-none shadow-lg shadow-primary/5 relative overflow-hidden group transition-all duration-300 hover:-translate-y-1 hover:shadow-primary/10">
      {/* Decorative background element */}
      <div className="absolute -top-10 -right-10 h-32 w-32 rounded-full bg-primary/10 blur-3xl transition-all duration-500 group-hover:bg-primary/20 group-hover:scale-150" />
      
      <div className="w-full text-left relative z-10">
        <p className="text-headline-sm font-bold text-on-surface uppercase tracking-tight">Profile</p>
      </div>

      <div className="flex flex-col items-center gap-2 relative z-10">
        <div className="flex items-baseline gap-1.5">
          <span className="text-display-sm font-black tracking-tighter text-on-surface">{profile.bmi.toFixed(1)}</span>
          <span className="text-label-md font-bold text-on-surface-variant/60 uppercase">BMI</span>
        </div>
        <div className={cn(
          "text-label-sm font-black uppercase px-4 py-1.5 rounded-full shadow-sm transition-all duration-500",
          profile.bmi_category === 'Normal' ? "bg-tertiary-container text-on-tertiary-container" : "bg-error-container text-on-error-container"
        )}>
          {profile.bmi_category}
        </div>
      </div>

      {/* Visual BMI Scale */}
      <div className="w-full space-y-4 mt-4 relative z-10">
        <div className="relative pt-6">
          {/* Current BMI Label */}
          <div 
            className="absolute -top-1 flex flex-col items-center transition-all duration-1000 ease-out"
            style={{ left: `${pct}%`, transform: 'translateX(-50%)' }}
          >
            <span className="bg-on-surface text-surface text-[10px] font-black px-1.5 py-0.5 rounded-sm shadow-sm animate-bounce-slow">YOU</span>
            <div className="w-[1px] h-2 bg-on-surface/50" />
          </div>

          <div className="relative h-2.5 w-full rounded-full bg-surface-container-highest overflow-hidden cursor-pointer shadow-inner">
            <div className="absolute inset-0 flex">
              <div 
                className="h-full w-[17.5%] bg-primary/20 hover:bg-primary/40 transition-colors" 
                onClick={() => setActiveLabel('Underweight (< 18.5)')}
                title="Underweight (< 18.5)"
              />
              <div 
                className="h-full w-[32.5%] bg-tertiary/40 hover:bg-tertiary/60 transition-colors" 
                onClick={() => setActiveLabel('Normal (18.5 - 25)')}
                title="Normal (18.5 - 25)"
              />
              <div 
                className="h-full w-[25%] bg-primary/40 hover:bg-primary/60 transition-colors" 
                onClick={() => setActiveLabel('Overweight (25 - 30)')}
                title="Overweight (25 - 30)"
              />
              <div 
                className="h-full w-[25%] bg-error/40 hover:bg-error/60 transition-colors" 
                onClick={() => setActiveLabel('Obese (> 30)')}
                title="Obese (> 30)"
              />
            </div>
            <div 
              className="absolute top-0 h-full w-1.5 bg-on-surface shadow-[0_0_12px_rgba(0,0,0,0.6)] z-20 transition-all duration-1000 ease-out pointer-events-none" 
              style={{ left: `${pct}%` }} 
            >
               <div className="absolute -top-1 -left-[2px] h-3.5 w-2.5 rounded-sm bg-on-surface/20 blur-[1px]" />
            </div>
          </div>
        </div>

        <div className="flex items-center justify-between text-[11px] font-black text-on-surface-variant/40 uppercase tracking-widest">
          <span>15</span>
          {activeLabel && (
            <span className="text-primary font-black animate-in fade-in zoom-in-95 duration-300">
              {activeLabel}
            </span>
          )}
          <span>35+</span>
        </div>
      </div>
    </Card>
  )
}

function HealthBackgroundSection({ lifestyle, medical, loading, onEdit }: any) {
  if (loading) return <Skeleton className="h-32" />
  
  const [isVisible, setIsVisible] = useState(false)
  const cardRef = useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => setIsVisible(entry.isIntersecting),
      { threshold: 0.5 }
    )
    const el = document.getElementById('health-background-section')
    if (el) observer.observe(el)
    return () => observer.disconnect()
  }, [])

  return (
    <Card id="health-background-section" className="flex flex-col gap-3 !p-4 bg-gradient-to-br from-surface to-surface-container-low overflow-visible">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <HeartPulse className="h-4 w-4 text-primary" />
          <h3 className="text-label-lg font-bold uppercase tracking-wider text-on-surface-variant">Health Background</h3>
        </div>
        <div className="relative">
          {/* Notification Label */}
          <div className={cn(
            "absolute -top-6 -right-2 z-20 whitespace-nowrap rounded-md bg-secondary-container px-2 py-0.5 text-[10px] font-black uppercase text-on-secondary-container shadow-md border border-secondary/20 transition-all duration-700",
            isVisible ? "translate-y-0 opacity-100 scale-100" : "translate-y-2 opacity-0 scale-90"
          )}>
            Edit Health Background
            <div className="absolute -bottom-1 right-3 h-2 w-2 rotate-45 bg-secondary-container border-b border-r border-secondary/20" />
          </div>
          
          <Button 
            variant="ghost" 
            size="sm" 
            className={cn(
              "h-8 w-8 rounded-full !p-0 transition-all duration-500",
              isVisible ? "bg-secondary-container text-on-secondary-container scale-110 shadow-lg shadow-secondary/20 border border-secondary/20" : "bg-surface-container text-on-surface-variant"
            )} 
            onClick={onEdit} 
            title="Edit Health Background"
          >
            <Plus className={cn("h-4 w-4 transition-transform duration-500", isVisible ? "rotate-180" : "rotate-0")} />
          </Button>
        </div>
      </div>

      <div className="flex flex-col gap-3">
        {/* Lifestyle Mini-stats */}
        {lifestyle ? (
          <div className="grid grid-cols-2 gap-2">
            <div className="flex flex-col rounded-lg bg-surface-container-high/50 p-2 border border-outline-variant/10">
              <span className="text-[9px] font-black uppercase text-on-surface-variant opacity-50">Tobacco</span>
              <span className="text-body-xs font-bold capitalize">{lifestyle.tobacco_type || 'None'}</span>
            </div>
            <div className="flex flex-col rounded-lg bg-surface-container-high/50 p-2 border border-outline-variant/10">
              <span className="text-[9px] font-black uppercase text-on-surface-variant opacity-50">Alcohol</span>
              <span className="text-body-xs font-bold capitalize">{lifestyle.alcohol_freq || 'None'}</span>
            </div>
          </div>
        ) : (
          <p className="text-[10px] italic text-on-surface-variant">No lifestyle data.</p>
        )}

        {/* Medical Tags */}
        <div className="flex flex-wrap gap-1.5">
          {medical ? (
            Object.entries(medical).map(([key, val]) => {
              if (typeof val !== 'boolean' || val === false) return null
              const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
              return (
                <span key={key} className="rounded-md bg-error-container/20 px-2 py-0.5 text-[10px] font-bold text-on-error-container border border-error/10">
                  {label}
                </span>
              )
            })
          ) : (
            <p className="text-[10px] italic text-on-surface-variant">No medical history.</p>
          )}
          {medical && Object.values(medical).every(v => v === false || typeof v !== 'boolean') && (
            <span className="text-[10px] text-on-surface-variant opacity-60">No conditions reported.</span>
          )}
        </div>
      </div>
    </Card>
  )
}

function HealthBackgroundModal({ open, onOpenChange, initialTab, lifestyleData, medicalData, onComplete }: any) {
  const [activeTab, setActiveTab] = useState<'lifestyle' | 'medical'>('lifestyle')

  useEffect(() => {
    if (open && initialTab) setActiveTab(initialTab)
  }, [open, initialTab])
  
  return (
    <Modal open={open} onClose={() => onOpenChange(false)} title="Health Background" className="max-w-2xl">
      <div className="flex flex-col gap-6">
        {/* Tab Slider */}
        <div className="relative flex rounded-xl bg-surface-container-high p-1">
          <div 
            className={cn(
              "absolute h-[calc(100%-8px)] w-[calc(50%-4px)] rounded-lg bg-surface shadow-sm transition-all duration-300 ease-in-out",
              activeTab === 'medical' ? "translate-x-full" : "translate-x-0"
            )}
          />
          <button 
            className={cn("relative z-10 flex-1 py-2 text-label-md font-bold transition-colors", activeTab === 'lifestyle' ? "text-primary" : "text-on-surface-variant")}
            onClick={() => setActiveTab('lifestyle')}
          >
            Lifestyle
          </button>
          <button 
            className={cn("relative z-10 flex-1 py-2 text-label-md font-bold transition-colors", activeTab === 'medical' ? "text-primary" : "text-on-surface-variant")}
            onClick={() => setActiveTab('medical')}
          >
            Medical History
          </button>
        </div>

        {/* Form Content */}
        <div className="min-h-[450px]">
          {activeTab === 'lifestyle' ? (
            <LifestyleFormContent initialData={lifestyleData} onComplete={() => { onComplete(); onOpenChange(false); }} />
          ) : (
            <MedicalHistoryFormContent initialData={medicalData} onComplete={() => { onComplete(); onOpenChange(false); }} />
          )}
        </div>
      </div>
    </Modal>
  )
}

function LifestyleFormContent({ initialData, onComplete }: any) {
  const create = useCreateLifestyle()
  const update = useUpdateLifestyle()
  
  const [tobaccoType, setTobaccoType] = useState(initialData?.tobacco_type ?? null)
  const [passiveSmoke, setPassiveSmoke] = useState<boolean | null>(initialData?.passive_smoke ?? null)
  const [alcoholFreq, setAlcoholFreq] = useState(initialData?.alcohol_freq ?? null)
  const [alcoholBinge, setAlcoholBinge] = useState<boolean | null>(initialData?.alcohol_binge ?? null)
  const [stressLevel, setStressLevel] = useState(initialData?.stress_level ?? null)
  const [workLifeBalance, setWorkLifeBalance] = useState(initialData?.work_life_balance ?? null)
  const [screenTimeHours, setScreenTimeHours] = useState(initialData?.screen_time_hours?.toString() ?? '')

  const handleSubmit = async () => {
    try {
      const body = {
        tobacco_type: tobaccoType,
        passive_smoke: passiveSmoke,
        alcohol_freq: alcoholFreq,
        alcohol_binge: alcoholBinge,
        stress_level: stressLevel,
        work_life_balance: workLifeBalance,
        screen_time_hours: screenTimeHours !== '' ? parseFloat(screenTimeHours) : null
      }
      if (initialData) await update.mutateAsync(body)
      else await create.mutateAsync(body)
      toast.success('Lifestyle profile updated')
      onComplete()
    } catch (e) {
      toast.error(getErrorMessage(e))
    }
  }

  return (
    <div className="flex flex-col gap-5">
      <Card className="!p-4 bg-surface-container-low/50">
        <div className="flex items-center gap-2 mb-3"><Cigarette className="h-4 w-4 text-primary" /> <span className="text-label-md font-bold">Tobacco Use</span></div>
        <div className="flex flex-wrap gap-2">
          {TOBACCO_OPTIONS.map(opt => (
            <Chip key={opt.value} selected={tobaccoType === opt.value} onClick={() => setTobaccoType(opt.value)}>{opt.label}</Chip>
          ))}
        </div>
        <div className="mt-3 flex items-center justify-between border-t border-outline-variant/10 pt-3">
          <span className="text-label-sm text-on-surface-variant">Passive smoking exposure?</span>
          <div className="flex gap-2">
            <Chip selected={passiveSmoke === true} onClick={() => setPassiveSmoke(true)}>Yes</Chip>
            <Chip selected={passiveSmoke === false} onClick={() => setPassiveSmoke(false)}>No</Chip>
          </div>
        </div>
      </Card>
      
      <Card className="!p-4 bg-surface-container-low/50">
        <div className="flex items-center gap-2 mb-3"><Wine className="h-4 w-4 text-primary" /> <span className="text-label-md font-bold">Alcohol Consumption</span></div>
        <Select value={alcoholFreq ?? ''} onChange={e => setAlcoholFreq(e.target.value || null)}>
          <option value="">Select frequency...</option>
          {ALCOHOL_OPTIONS.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
        </Select>
        <div className="mt-3 flex items-center justify-between border-t border-outline-variant/10 pt-3">
          <span className="text-label-sm text-on-surface-variant">Occasional binge drinking?</span>
          <div className="flex gap-2">
            <Chip selected={alcoholBinge === true} onClick={() => setAlcoholBinge(true)}>Yes</Chip>
            <Chip selected={alcoholBinge === false} onClick={() => setAlcoholBinge(false)}>No</Chip>
          </div>
        </div>
      </Card>

      <Card className="!p-4 bg-surface-container-low/50">
        <div className="flex items-center gap-2 mb-3"><Brain className="h-4 w-4 text-primary" /> <span className="text-label-md font-bold">Mental Wellness (1-5)</span></div>
        <div className="flex flex-col gap-4">
          <div className="flex flex-col gap-2">
            <span className="text-[10px] uppercase font-bold text-on-surface-variant opacity-60">Stress Level</span>
            <div className="flex gap-2">
              {[1,2,3,4,5].map(n => <Chip key={n} selected={stressLevel === n} onClick={() => setStressLevel(n)}>{n}</Chip>)}
            </div>
          </div>
          <div className="flex flex-col gap-2">
            <span className="text-[10px] uppercase font-bold text-on-surface-variant opacity-60">Work-Life Balance</span>
            <div className="flex gap-2">
              {[1,2,3,4,5].map(n => <Chip key={n} selected={workLifeBalance === n} onClick={() => setWorkLifeBalance(n)}>{n}</Chip>)}
            </div>
          </div>
        </div>
      </Card>

      <Card className="!p-4 bg-surface-container-low/50">
        <div className="flex items-center gap-2 mb-3"><Monitor className="h-4 w-4 text-primary" /> <span className="text-label-md font-bold">Daily Screen Time</span></div>
        <Input type="number" placeholder="Hours per day" value={screenTimeHours} onChange={e => setScreenTimeHours(e.target.value)} />
      </Card>

      <Button onClick={handleSubmit} loading={create.isPending || update.isPending} className="w-full mt-2">Save Profile</Button>
    </div>
  )
}

function MedicalHistoryFormContent({ initialData, onComplete }: any) {
  const create = useCreateMedicalHistory()
  const update = useUpdateMedicalHistory()
  const [conditions, setConditions] = useState<Record<string, boolean>>(
    MEDICAL_CONDITIONS.reduce((acc, c) => ({ ...acc, [c.key]: !!initialData?.[c.key] }), {})
  )

  const handleSubmit = async () => {
    try {
      if (initialData) await update.mutateAsync(conditions)
      else await create.mutateAsync(conditions)
      toast.success('Medical history updated')
      onComplete()
    } catch (e) {
      toast.error(getErrorMessage(e))
    }
  }

  return (
    <div className="flex flex-col gap-3">
      {MEDICAL_CONDITIONS.map(c => (
        <Card key={c.key} className="!p-4 flex items-center justify-between border-primary/5">
          <div className="min-w-0">
            <p className="text-label-md font-bold text-on-surface">{c.label}</p>
            <p className="text-body-xs text-on-surface-variant line-clamp-1">{c.description}</p>
          </div>
          <div className="flex gap-2">
            <button 
              onClick={() => setConditions(p => ({...p, [c.key]: true}))} 
              className={cn("h-10 w-10 rounded-xl flex items-center justify-center transition-all", conditions[c.key] ? "bg-error text-white shadow-lg shadow-error/20" : "bg-surface-container hover:bg-surface-container-high")}
            >
              <Check className="h-5 w-5" />
            </button>
            <button 
              onClick={() => setConditions(p => ({...p, [c.key]: false}))} 
              className={cn("h-10 w-10 rounded-xl flex items-center justify-center transition-all", conditions[c.key] === false ? "bg-tertiary text-white shadow-lg shadow-tertiary/20" : "bg-surface-container hover:bg-surface-container-high")}
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </Card>
      ))}
      <Button onClick={handleSubmit} loading={create.isPending || update.isPending} className="w-full mt-4">Update Medical History</Button>
    </div>
  )
}

function InfoItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col">
      <span className="text-label-sm uppercase text-on-surface-variant">{label}</span>
      <span className="text-body-md font-semibold text-on-surface">{value}</span>
    </div>
  )
}
