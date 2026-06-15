import { useEffect, useState, useMemo } from 'react'
import { toast } from 'sonner'
import { Modal } from '@/components/ui/Modal'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { useCreateMedicalHistory, useUpdateMedicalHistory } from './api'
import { getErrorMessage } from '@/lib/api'
import { MEDICAL_CONDITIONS, type MedicalHistoryCreate, type MedicalHistoryResponse } from '@/types/api'
import { HeartPulse, Check, X as XIcon } from 'lucide-react'
import { cn } from '@/lib/utils'

interface Props {
  open: boolean
  onComplete: () => void
  initialData?: MedicalHistoryResponse | null
}

export function MedicalHistoryModal({ open, onComplete, initialData }: Props) {
  const create = useCreateMedicalHistory()
  const update = useUpdateMedicalHistory()
  const [conditions, setConditions] = useState<Record<string, boolean | null>>({})

  useEffect(() => {
    if (open && initialData) {
      const initialConditions: Record<string, boolean | null> = {}
      MEDICAL_CONDITIONS.forEach((c) => {
        initialConditions[c.key] = (initialData as any)[c.key]
      })
      setConditions(initialConditions)
    } else if (open && !initialData) {
      setConditions({})
    }
  }, [open, initialData])

  const hasAnyField = useMemo(() => {
    return Object.values(conditions).some((v) => v !== null && v !== undefined)
  }, [conditions])

  const toggleCondition = (key: string, value: boolean) => {
    setConditions((prev) => ({
      ...prev,
      [key]: prev[key] === value ? null : value,
    }))
  }

  const handleSubmit = async () => {
    const body: Record<string, boolean | null> = {}
    MEDICAL_CONDITIONS.forEach((c) => {
      body[c.key] = conditions[c.key] ?? null
    })

    try {
      if (initialData) {
        await update.mutateAsync(body as Partial<MedicalHistoryCreate>)
        toast.success('Medical history updated!')
      } else {
        await create.mutateAsync(body as MedicalHistoryCreate)
        toast.success('Medical history saved!')
      }
      onComplete()
    } catch (e) {
      toast.error(getErrorMessage(e))
    }
  }

  const handleSkip = () => {
    onComplete()
  }

  const isPending = create.isPending || update.isPending

  return (
    <Modal open={open} onClose={handleSkip} title={initialData ? "Update Medical History" : "Medical History"} className="max-w-lg">
      <div className="flex flex-col gap-5 pb-2">
        <p className="text-body-md text-on-surface-variant">
          {initialData 
            ? "Update your medical conditions to keep your health insights accurate."
            : "Do you have any of these conditions? This helps us tailor health insights to your needs."}
        </p>

        <div className="flex flex-col gap-3">
          {MEDICAL_CONDITIONS.map((condition) => {
            const value = conditions[condition.key] ?? null
            return (
              <Card key={condition.key} className="!p-4">
                <div className="flex items-center justify-between gap-4">
                  <div className="flex items-center gap-3 min-w-0">
                    <HeartPulse className="h-5 w-5 shrink-0 text-on-surface-variant" />
                    <div className="min-w-0">
                      <p className="text-label-lg text-on-surface">{condition.label}</p>
                      <p className="text-body-sm text-on-surface-variant">{condition.description}</p>
                    </div>
                  </div>
                  <div className="flex shrink-0 gap-1.5">
                    <button
                      type="button"
                      onClick={() => toggleCondition(condition.key, true)}
                      className={cn(
                        'flex h-9 w-9 items-center justify-center rounded-lg transition-colors',
                        value === true
                          ? 'bg-error text-error-on'
                          : 'bg-surface-container text-on-surface-variant hover:bg-surface-container-high'
                      )}
                      aria-label={`Yes, I have ${condition.label}`}
                    >
                      <Check className="h-4 w-4" />
                    </button>
                    <button
                      type="button"
                      onClick={() => toggleCondition(condition.key, false)}
                      className={cn(
                        'flex h-9 w-9 items-center justify-center rounded-lg transition-colors',
                        value === false
                          ? 'bg-tertiary text-tertiary-on'
                          : 'bg-surface-container text-on-surface-variant hover:bg-surface-container-high'
                      )}
                      aria-label={`No, I don't have ${condition.label}`}
                    >
                      <XIcon className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </Card>
            )
          })}
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-end gap-3 pt-2">
          <Button variant="ghost" onClick={handleSkip} disabled={isPending}>
            {initialData ? 'Cancel' : 'Skip'}
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={!hasAnyField}
            loading={isPending}
            className={!hasAnyField ? 'opacity-50' : ''}
          >
            {initialData ? 'Update' : 'Submit'}
          </Button>
        </div>
      </div>
    </Modal>
  )
}
