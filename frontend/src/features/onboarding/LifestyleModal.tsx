import { useEffect, useState, useMemo } from 'react'
import { toast } from 'sonner'
import { Modal } from '@/components/ui/Modal'
import { Button } from '@/components/ui/Button'
import { Chip } from '@/components/ui/Chip'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Card } from '@/components/ui/Card'
import { useCreateLifestyle, useUpdateLifestyle } from './api'
import { getErrorMessage } from '@/lib/api'
import {
  TOBACCO_OPTIONS,
  ALCOHOL_OPTIONS,
  type TobaccoType,
  type AlcoholFreq,
  type LifestyleResponse,
} from '@/types/api'
import {
  Cigarette,
  Wine,
  Brain,
  Monitor,
  Wind,
} from 'lucide-react'

interface Props {
  open: boolean
  onComplete: () => void
  initialData?: LifestyleResponse | null
}

export function LifestyleModal({ open, onComplete, initialData }: Props) {
  const create = useCreateLifestyle()
  const update = useUpdateLifestyle()

  const [tobaccoType, setTobaccoType] = useState<TobaccoType | null>(null)
  const [passiveSmoke, setPassiveSmoke] = useState<boolean | null>(null)
  const [alcoholFreq, setAlcoholFreq] = useState<AlcoholFreq | null>(null)
  const [alcoholBinge, setAlcoholBinge] = useState<boolean | null>(null)
  const [stressLevel, setStressLevel] = useState<number | null>(null)
  const [workLifeBalance, setWorkLifeBalance] = useState<number | null>(null)
  const [screenTimeHours, setScreenTimeHours] = useState<string>('')

  useEffect(() => {
    if (open && initialData) {
      setTobaccoType(initialData.tobacco_type)
      setPassiveSmoke(initialData.passive_smoke)
      setAlcoholFreq(initialData.alcohol_freq)
      setAlcoholBinge(initialData.alcohol_binge)
      setStressLevel(initialData.stress_level)
      setWorkLifeBalance(initialData.work_life_balance)
      setScreenTimeHours(initialData.screen_time_hours?.toString() ?? '')
    } else if (open && !initialData) {
      setTobaccoType(null)
      setPassiveSmoke(null)
      setAlcoholFreq(null)
      setAlcoholBinge(null)
      setStressLevel(null)
      setWorkLifeBalance(null)
      setScreenTimeHours('')
    }
  }, [open, initialData])

  const hasAnyField = useMemo(() => {
    return (
      tobaccoType !== null ||
      passiveSmoke !== null ||
      alcoholFreq !== null ||
      alcoholBinge !== null ||
      stressLevel !== null ||
      workLifeBalance !== null ||
      screenTimeHours !== ''
    )
  }, [tobaccoType, passiveSmoke, alcoholFreq, alcoholBinge, stressLevel, workLifeBalance, screenTimeHours])

  const handleSubmit = async () => {
    const body: Record<string, unknown> = {
      tobacco_type: tobaccoType,
      passive_smoke: passiveSmoke,
      alcohol_freq: alcoholFreq,
      alcohol_binge: alcoholBinge,
      stress_level: stressLevel,
      work_life_balance: workLifeBalance,
      screen_time_hours: screenTimeHours !== '' ? parseFloat(screenTimeHours) : null,
    }

    try {
      if (initialData) {
        await update.mutateAsync(body)
        toast.success('Lifestyle profile updated!')
      } else {
        await create.mutateAsync(body)
        toast.success('Lifestyle profile created!')
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
    <Modal open={open} onClose={handleSkip} title={initialData ? "Update Lifestyle" : "Your Lifestyle"} className="max-w-2xl">
      <div className="flex flex-col gap-6 pb-2">
        <p className="text-body-md text-on-surface-variant">
          {initialData 
            ? "Update your lifestyle habits to keep your health insights accurate."
            : "Help us personalize your health insights by sharing your lifestyle habits. You can skip this and add it later."}
        </p>

        {/* Tobacco */}
        <Card className="flex flex-col gap-3 !p-4">
          <div className="flex items-center gap-2">
            <Cigarette className="h-5 w-5 text-on-surface-variant" />
            <span className="text-label-lg text-on-surface">Tobacco Use</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {TOBACCO_OPTIONS.map((opt) => (
              <Chip
                key={opt.value}
                selected={tobaccoType === opt.value}
                onClick={() => setTobaccoType(tobaccoType === opt.value ? null : opt.value)}
              >
                {opt.label}
              </Chip>
            ))}
          </div>
        </Card>

        {/* Passive Smoke */}
        <Card className="flex flex-col gap-3 !p-4">
          <div className="flex items-center gap-2">
            <Wind className="h-5 w-5 text-on-surface-variant" />
            <span className="text-label-lg text-on-surface">Passive Smoke Exposure</span>
          </div>
          <div className="flex gap-2">
            <Chip selected={passiveSmoke === true} onClick={() => setPassiveSmoke(passiveSmoke === true ? null : true)}>
              Yes
            </Chip>
            <Chip selected={passiveSmoke === false} onClick={() => setPassiveSmoke(passiveSmoke === false ? null : false)}>
              No
            </Chip>
          </div>
        </Card>

        {/* Alcohol */}
        <Card className="flex flex-col gap-3 !p-4">
          <div className="flex items-center gap-2">
            <Wine className="h-5 w-5 text-on-surface-variant" />
            <span className="text-label-lg text-on-surface">Alcohol Consumption</span>
          </div>
          <Select
            label="Frequency"
            value={alcoholFreq ?? ''}
            onChange={(e) => setAlcoholFreq(e.target.value === '' ? null : (e.target.value as AlcoholFreq))}
          >
            <option value="">Select...</option>
            {ALCOHOL_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </Select>
          <div className="flex flex-col gap-1.5">
            <span className="text-label-lg text-on-surface-variant">Occasional binge drinking?</span>
            <div className="flex gap-2">
              <Chip selected={alcoholBinge === true} onClick={() => setAlcoholBinge(alcoholBinge === true ? null : true)}>
                Yes
              </Chip>
              <Chip selected={alcoholBinge === false} onClick={() => setAlcoholBinge(alcoholBinge === false ? null : false)}>
                No
              </Chip>
            </div>
          </div>
        </Card>

        {/* Stress & Work-Life Balance */}
        <Card className="flex flex-col gap-4 !p-4">
          <div className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-on-surface-variant" />
            <span className="text-label-lg text-on-surface">Mental Wellness</span>
          </div>
          <div className="flex flex-col gap-1.5">
            <span className="text-label-lg text-on-surface-variant">
              Stress Level <span className="text-body-sm">(1 = Low, 5 = High)</span>
            </span>
            <div className="flex gap-2">
              {[1, 2, 3, 4, 5].map((n) => (
                <Chip key={n} selected={stressLevel === n} onClick={() => setStressLevel(stressLevel === n ? null : n)}>
                  {n}
                </Chip>
              ))}
            </div>
          </div>
          <div className="flex flex-col gap-1.5">
            <span className="text-label-lg text-on-surface-variant">
              Work-Life Balance <span className="text-body-sm">(1 = Poor, 5 = Excellent)</span>
            </span>
            <div className="flex gap-2">
              {[1, 2, 3, 4, 5].map((n) => (
                <Chip
                  key={n}
                  selected={workLifeBalance === n}
                  onClick={() => setWorkLifeBalance(workLifeBalance === n ? null : n)}
                >
                  {n}
                </Chip>
              ))}
            </div>
          </div>
        </Card>

        {/* Screen Time */}
        <Card className="flex flex-col gap-3 !p-4">
          <div className="flex items-center gap-2">
            <Monitor className="h-5 w-5 text-on-surface-variant" />
            <span className="text-label-lg text-on-surface">Screen Time</span>
          </div>
          <Input
            label="Daily hours"
            type="number"
            step="0.5"
            min={0}
            max={24}
            placeholder="e.g. 6"
            value={screenTimeHours}
            onChange={(e) => setScreenTimeHours(e.target.value)}
          />
        </Card>

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
