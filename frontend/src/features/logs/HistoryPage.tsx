import { useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { ChevronLeft, ChevronRight, Footprints, Moon, Droplet, UtensilsCrossed, Trash2, Pencil, Calendar, Clock, Timer, Apple, Candy } from 'lucide-react'
import { format, subDays } from 'date-fns'
import { toast } from 'sonner'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Skeleton } from '@/components/ui/Skeleton'
import { Chip } from '@/components/ui/Chip'
import { Modal } from '@/components/ui/Modal'
import { EmptyState } from '@/components/ui/EmptyState'
import { useAllLogs, useDeleteLog, useRangeLogs, useUpdateLog } from './api'
import { LogEntryForm } from './LogEntryForm'
import { formatNumber } from '@/lib/utils'
import { getErrorMessage } from '@/lib/api'
import type { DailyHealthLog } from '@/types/api'

type Mode = 'all' | 'range'

export function HistoryPage() {
  const [params, setParams] = useSearchParams()
  const mode = (params.get('mode') as Mode) ?? 'all'
  const page = Number(params.get('page') ?? 1)
  const limit = Number(params.get('limit') ?? 20)
  const start = params.get('from') ?? format(subDays(new Date(), 30), 'yyyy-MM-dd')
  const end = params.get('to') ?? format(new Date(), 'yyyy-MM-dd')

  const setParamsMultiple = (updates: Record<string, string | number>) => {
    const next = new URLSearchParams(params)
    Object.entries(updates).forEach(([k, v]) => {
      next.set(k, String(v))
    })
    setParams(next, { replace: true })
  }

  const setParam = (k: string, v: string | number) => {
    setParamsMultiple({ [k]: v })
  }

  const all = useAllLogs(page, limit, mode === 'all')
  const range = useRangeLogs(start, end, page, limit, mode === 'range')
  const query = mode === 'range' ? range : all

  const [editing, setEditing] = useState<DailyHealthLog | null>(null)
  const [deleting, setDeleting] = useState<DailyHealthLog | null>(null)
  const updateLog = useUpdateLog(editing?.id ?? 0)
  const delLog = useDeleteLog()

  const totalPages = useMemo(() => {
    if (!query.data) return 1
    return Math.max(1, Math.ceil(query.data.total / limit))
  }, [query.data, limit])

  return (
    <div>
      <h1 className="text-headline-xl text-on-surface">History</h1>
      <p className="mt-1 text-body-md text-on-surface-variant">Browse and edit your past logs.</p>

      <Card className="mt-md flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div className="flex flex-wrap items-center gap-2">
          <Chip selected={mode === 'all'} onClick={() => setParamsMultiple({ mode: 'all', page: 1 })}>All</Chip>
          <Chip selected={mode === 'range'} onClick={() => setParamsMultiple({ mode: 'range', page: 1 })}>Date range</Chip>
        </div>
        {mode === 'range' && (
          <div className="flex flex-wrap items-center gap-2">
            <div className="flex items-center gap-1.5 rounded-lg bg-surface-container-low px-3 py-2">
              <Calendar className="h-4 w-4 text-on-surface-variant" />
              <input type="date" value={start} onChange={(e) => setParam('from', e.target.value)} className="bg-transparent text-body-sm outline-none" />
            </div>
            <span className="text-on-surface-variant">→</span>
            <div className="flex items-center gap-1.5 rounded-lg bg-surface-container-low px-3 py-2">
              <Calendar className="h-4 w-4 text-on-surface-variant" />
              <input type="date" value={end} onChange={(e) => setParam('to', e.target.value)} className="bg-transparent text-body-sm outline-none" />
            </div>
          </div>
        )}
        <div className="flex items-center gap-2">
          <span className="text-body-sm text-on-surface-variant">Per page</span>
          <select
            value={limit}
            onChange={(e) => { setParam('limit', e.target.value); setParam('page', 1) }}
            className="rounded-lg bg-surface-container-low px-3 py-2 text-body-sm outline-none"
          >
            {[10, 20, 50].map((n) => <option key={n} value={n}>{n}</option>)}
          </select>
        </div>
      </Card>

      <div className="mt-md flex flex-col gap-3">
        {query.isError && (
          <Card className="border-error/30 bg-error/5">
            <p className="text-center text-body-md text-error">{getErrorMessage(query.error)}</p>
          </Card>
        )}
        {query.isLoading && Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-24" />)}
        {query.isSuccess && query.data.logs.length === 0 && (
          <EmptyState title="No logs yet" description="Once you start logging, your entries appear here." />
        )}
        {query.data?.logs.map((log) => (
          <Card key={log.id} className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex flex-wrap items-center gap-md">
              <div>
                <p className="text-label-lg uppercase text-on-surface-variant">{format(new Date(log.log_date), 'EEE')}</p>
                <p className="text-headline-md text-on-surface">{format(new Date(log.log_date), 'MMM d')}</p>
              </div>
              <Metric icon={<Footprints className="h-4 w-4" />} value={log.steps !== null ? formatNumber(log.steps) : '—'} label="steps" />
              <Metric icon={<Moon className="h-4 w-4" />} value={log.sleep_hours !== null ? `${log.sleep_hours}h` : '—'} label="sleep" />
              <Metric icon={<Droplet className="h-4 w-4" />} value={log.water_intake !== null ? `${log.water_intake}L` : '—'} label="water" />
              <Metric icon={<UtensilsCrossed className="h-4 w-4" />} value={`${log.food_log?.length ?? 0}`} label="meals" />
              <Metric icon={<Clock className="h-4 w-4" />} value={log.activity_minutes !== null ? `${log.activity_minutes}m` : '—'} label="active" />
              <Metric icon={<Candy className="h-4 w-4" />} value={log.nutrition_sugar !== null ? `${log.nutrition_sugar}g` : '—'} label="sugar" />
            </div>
            <div className="flex gap-2">
              <Button variant="ghost" size="sm" onClick={() => setEditing(log)}><Pencil className="h-4 w-4" /></Button>
              <Button variant="ghost" size="sm" onClick={() => setDeleting(log)}><Trash2 className="h-4 w-4" /></Button>
            </div>
          </Card>
        ))}
      </div>

      {query.data && query.data.total > 0 && (
        <div className="mt-md flex items-center justify-between">
          <p className="text-body-sm text-on-surface-variant">
            {(page - 1) * limit + 1}–{Math.min(page * limit, query.data.total)} of {query.data.total}
          </p>
          <div className="flex items-center gap-1">
            <Button variant="ghost" size="sm" disabled={page <= 1} onClick={() => setParam('page', page - 1)}>
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <span className="px-2 text-body-sm">{page} / {totalPages}</span>
            <Button variant="ghost" size="sm" disabled={page >= totalPages} onClick={() => setParam('page', page + 1)}>
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}

      {/* Edit modal */}
      <Modal open={!!editing} onClose={() => setEditing(null)} title={editing ? `Edit ${format(new Date(editing.log_date), 'MMM d, yyyy')}` : ''} className="max-w-2xl">
        {editing && (
          <LogEntryForm
            initial={editing}
            submitting={updateLog.isPending}
            submitLabel="Save changes"
            onSubmit={async (body) => {
              await updateLog.mutateAsync(body)
              setEditing(null)
            }}
          />
        )}
      </Modal>

      {/* Delete confirm */}
      <Modal open={!!deleting} onClose={() => setDeleting(null)} title="Delete log?">
        <p className="text-body-md text-on-surface-variant">
          {deleting && `Remove the entry for ${format(new Date(deleting.log_date), 'MMM d, yyyy')}?`}
        </p>
        <div className="mt-md flex justify-end gap-2">
          <Button variant="ghost" onClick={() => setDeleting(null)}>Cancel</Button>
          <Button
            variant="destructive"
            loading={delLog.isPending}
            onClick={async () => {
              if (!deleting) return
              try {
                await delLog.mutateAsync(deleting.id)
                toast.success('Log deleted')
                setDeleting(null)
              } catch (e) {
                toast.error(getErrorMessage(e))
              }
            }}
          >
            Delete
          </Button>
        </div>
      </Modal>
    </div>
  )
}

function Metric({ icon, value, label }: { icon: React.ReactNode; value: string; label: string }) {
  return (
    <div className="flex items-center gap-1.5 text-body-sm text-on-surface-variant">
      {icon}
      <span className="font-semibold text-on-surface">{value}</span>
      <span>{label}</span>
    </div>
  )
}
