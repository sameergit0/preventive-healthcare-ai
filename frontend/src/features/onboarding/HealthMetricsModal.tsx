import { useState, useMemo } from 'react'
import { toast } from 'sonner'
import { Modal } from '@/components/ui/Modal'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Chip } from '@/components/ui/Chip'
import { Stepper } from '@/components/ui/Stepper'
import { useUpsertTodayLog } from '@/features/logs/api'
import { getErrorMessage } from '@/lib/api'
import type { DailyHealthLogCreate } from '@/types/api'
import {
  Footprints,
  Moon,
  Droplet,
  Clock,
} from 'lucide-react'

type SleepQuality = 'poor' | 'average' | 'good' | 'excellent'

const SLEEP_QUALITIES: { value: SleepQuality; label: string }[] = [
  { value: 'poor', label: 'Poor' },
  { value: 'average', label: 'Average' },
  { value: 'good', label: 'Good' },
  { value: 'excellent', label: 'Excellent' },
]

interface Props {
  open: boolean
  onComplete: () => void
}

export function HealthMetricsModal({ open, onComplete }: Props) {
  const upsert = useUpsertTodayLog()

  const [steps, setSteps] = useState(0)
  const [stepsActive, setStepsActive] = useState(false)

  const [sleepHours, setSleepHours] = useState(0)
  const [sleepActive, setSleepActive] = useState(false)

  const [waterIntake, setWaterIntake] = useState(0)
  const [waterActive, setWaterActive] = useState(false)

  const [activityMinutes, setActivityMinutes] = useState(0)
  const [activityActive, setActivityActive] = useState(false)

  const [sleepQuality, setSleepQuality] = useState<SleepQuality | null>(null)

  const hasAnyField = useMemo(() => {
    return (
      (stepsActive && steps > 0) ||
      (sleepActive && sleepHours > 0) ||
      (waterActive && waterIntake > 0) ||
      (activityActive && activityMinutes > 0) ||
      sleepQuality !== null
    )
  }, [steps, stepsActive, sleepHours, sleepActive, waterIntake, waterActive, activityMinutes, activityActive, sleepQuality])

  const handleSubmit = async () => {
    const body: DailyHealthLogCreate = {}
    if (stepsActive && steps > 0) body.steps = steps
    if (sleepActive && sleepHours > 0) body.sleep_hours = sleepHours
    if (waterActive && waterIntake > 0) body.water_intake = waterIntake / 10 // stored in liters, stepper uses 0.1L steps
    if (activityActive && activityMinutes > 0) body.activity_minutes = activityMinutes
    if (sleepQuality !== null) body.sleep_quality = sleepQuality

    try {
      await upsert.mutateAsync(body)
      toast.success("Today's health metrics saved!")
      onComplete()
    } catch (e) {
      toast.error(getErrorMessage(e))
    }
  }

  const handleSkip = () => {
    onComplete()
  }

  return (
    <Modal open={open} onClose={handleSkip} title="Today's Health" className="max-w-lg">
      <div className="flex flex-col gap-5 pb-2">
        <p className="text-body-md text-on-surface-variant">
          Log your health metrics for today. You can always update these later from the dashboard.
        </p>

        {/* Steps */}
        <Card className="flex flex-col gap-3 !p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Footprints className="h-5 w-5 text-on-surface-variant" />
              <span className="text-label-lg text-on-surface">Steps</span>
            </div>
            <Chip
              selected={stepsActive}
              onClick={() => { setStepsActive(!stepsActive); if (stepsActive) setSteps(0) }}
            >
              {stepsActive ? 'Active' : 'Track'}
            </Chip>
          </div>
          {stepsActive && (
            <Stepper value={steps} onChange={setSteps} step={500} min={0} max={100000} unit="steps" />
          )}
        </Card>

        {/* Sleep */}
        <Card className="flex flex-col gap-3 !p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Moon className="h-5 w-5 text-on-surface-variant" />
              <span className="text-label-lg text-on-surface">Sleep</span>
            </div>
            <Chip
              selected={sleepActive}
              onClick={() => { setSleepActive(!sleepActive); if (sleepActive) setSleepHours(0) }}
            >
              {sleepActive ? 'Active' : 'Track'}
            </Chip>
          </div>
          {sleepActive && (
            <>
              <Stepper value={sleepHours} onChange={setSleepHours} step={0.5} min={0} max={24} unit="hours" />
              <div className="flex flex-col gap-1.5">
                <span className="text-label-lg text-on-surface-variant">Quality</span>
                <div className="flex flex-wrap gap-2">
                  {SLEEP_QUALITIES.map((sq) => (
                    <Chip
                      key={sq.value}
                      selected={sleepQuality === sq.value}
                      onClick={() => setSleepQuality(sleepQuality === sq.value ? null : sq.value)}
                    >
                      {sq.label}
                    </Chip>
                  ))}
                </div>
              </div>
            </>
          )}
        </Card>

        {/* Water */}
        <Card className="flex flex-col gap-3 !p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Droplet className="h-5 w-5 text-on-surface-variant" />
              <span className="text-label-lg text-on-surface">Water</span>
            </div>
            <Chip
              selected={waterActive}
              onClick={() => { setWaterActive(!waterActive); if (waterActive) setWaterIntake(0) }}
            >
              {waterActive ? 'Active' : 'Track'}
            </Chip>
          </div>
          {waterActive && (
            <Stepper value={waterIntake} onChange={setWaterIntake} step={1} min={0} max={100} unit="× 0.1 L" />
          )}
        </Card>

        {/* Activity */}
        <Card className="flex flex-col gap-3 !p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-on-surface-variant" />
              <span className="text-label-lg text-on-surface">Activity</span>
            </div>
            <Chip
              selected={activityActive}
              onClick={() => { setActivityActive(!activityActive); if (activityActive) setActivityMinutes(0) }}
            >
              {activityActive ? 'Active' : 'Track'}
            </Chip>
          </div>
          {activityActive && (
            <Stepper value={activityMinutes} onChange={setActivityMinutes} step={5} min={0} max={1440} unit="min" />
          )}
        </Card>

        {/* Action Buttons */}
        <div className="flex items-center justify-end gap-3 pt-2">
          <Button variant="ghost" onClick={handleSkip} disabled={upsert.isPending}>
            Skip
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={!hasAnyField}
            loading={upsert.isPending}
            className={!hasAnyField ? 'opacity-50' : ''}
          >
            Submit
          </Button>
        </div>
      </div>
    </Modal>
  )
}
