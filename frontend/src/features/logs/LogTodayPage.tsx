import { useState } from 'react'
import { Trash2 } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/Button'
import { Modal } from '@/components/ui/Modal'
import { Spinner } from '@/components/ui/Spinner'
import { LogEntryForm } from './LogEntryForm'
import { useDeleteToday, useTodayLog, useUpsertTodayLog } from './api'
import { getErrorMessage } from '@/lib/api'

export function LogTodayPage() {
  const today = useTodayLog()
  const upsert = useUpsertTodayLog()
  const del = useDeleteToday()
  const [confirm, setConfirm] = useState(false)

  const log = today.data?.logs[0] ?? null

  if (today.isLoading) {
    return <div className="flex justify-center py-lg"><Spinner /></div>
  }

  return (
    <div className="mx-auto max-w-2xl">
      <div className="flex items-end justify-between gap-4">
        <div>
          <h1 className="text-headline-xl text-on-surface">Today's log</h1>
          <p className="mt-1 text-body-md text-on-surface-variant">
            {log ? 'Edit any field to update today\'s entry.' : 'Capture how your day is going.'}
          </p>
        </div>
        {log && (
          <Button variant="ghost" size="sm" onClick={() => setConfirm(true)}>
            <Trash2 className="h-4 w-4" /> Delete
          </Button>
        )}
      </div>
      <div className="mt-md">
        <LogEntryForm
          initial={log}
          submitting={upsert.isPending}
          onSubmit={(body) => upsert.mutateAsync(body)}
        />
      </div>
      <Modal open={confirm} onClose={() => setConfirm(false)} title="Delete today's log?">
        <p className="text-body-md text-on-surface-variant">All metrics for today will be removed.</p>
        <div className="mt-md flex justify-end gap-2">
          <Button variant="ghost" onClick={() => setConfirm(false)}>Cancel</Button>
          <Button
            variant="destructive"
            loading={del.isPending}
            onClick={async () => {
              try {
                await del.mutateAsync()
                toast.success('Today\'s log deleted')
                setConfirm(false)
              } catch (e) {
                toast.error(getErrorMessage(e))
              }
            }}
          >
            Yes, delete
          </Button>
        </div>
      </Modal>
    </div>
  )
}
