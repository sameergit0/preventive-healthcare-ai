import { useEffect, useState } from 'react'
import { Footprints, Moon, Droplet, UtensilsCrossed, Plus, X } from 'lucide-react'
import { toast } from 'sonner'
import { Card } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import type { DailyHealthLog, DailyHealthLogCreate, FoodItem, Meal } from '@/types/api'
import { getErrorMessage } from '@/lib/api'

const MEALS: Meal[] = ['breakfast', 'lunch', 'dinner']
export type LogField = 'steps' | 'sleep' | 'water' | 'food'

interface LogEntryFormProps {
  initial?: DailyHealthLog | null
  onSubmit: (body: DailyHealthLogCreate) => Promise<unknown>
  submitting?: boolean
  submitLabel?: string
  fields?: LogField[]
}

export function LogEntryForm({ initial, onSubmit, submitting, submitLabel = 'Save log', fields }: LogEntryFormProps) {
  const [steps, setSteps] = useState<string>('')
  const [sleep, setSleep] = useState<string>('')
  const [water, setWater] = useState<string>('')
  const [food, setFood] = useState<Record<Meal, string[]>>({ breakfast: [], lunch: [], dinner: [] })
  const [drafts, setDrafts] = useState<Record<Meal, string>>({ breakfast: '', lunch: '', dinner: '' })

  useEffect(() => {
    if (!initial) return
    setSteps(initial.steps?.toString() ?? '')
    setSleep(initial.sleep_hours?.toString() ?? '')
    setWater(initial.water_intake?.toString() ?? '')
    const next: Record<Meal, string[]> = { breakfast: [], lunch: [], dinner: [] }
    initial.food_log?.forEach((f) => {
      next[f.meal] = [...f.items]
    })
    setFood(next)
  }, [initial])

  const addFoodItem = (meal: Meal) => {
    const v = drafts[meal].trim()
    if (!v) return
    setFood((f) => ({ ...f, [meal]: [...f[meal], v] }))
    setDrafts((d) => ({ ...d, [meal]: '' }))
  }

  const removeFoodItem = (meal: Meal, idx: number) => {
    setFood((f) => ({ ...f, [meal]: f[meal].filter((_, i) => i !== idx) }))
  }

  const addWaterGlass = () => {
    const cur = parseFloat(water || '0')
    setWater((cur + 0.25).toFixed(2).replace(/\.?0+$/, ''))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const body: DailyHealthLogCreate = {}
    if (steps !== '') body.steps = Number(steps)
    if (sleep !== '') body.sleep_hours = Number(sleep)
    if (water !== '') body.water_intake = Number(water)
    const food_log: FoodItem[] = MEALS.filter((m) => food[m].length > 0).map((m) => ({ meal: m, items: food[m] }))
    if (food_log.length > 0) body.food_log = food_log

    if (Object.keys(body).length === 0) {
      toast.error('Add at least one metric')
      return
    }
    try {
      await onSubmit(body)
      toast.success('Log saved')
    } catch (err) {
      toast.error(getErrorMessage(err))
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-md">
      {(!fields || fields.includes('steps')) && (
        <Card>
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-secondary-fixed text-on-secondary-fixed-variant">
            <Footprints className="h-6 w-6" />
          </div>
          <h3 className="text-headline-md text-on-surface">Steps</h3>
        </div>
        <div className="mt-3 flex flex-col gap-3 sm:flex-row sm:items-end">
          <Input
            type="number"
            min={0}
            max={100000}
            value={steps}
            onChange={(e) => setSteps(e.target.value)}
            placeholder="0"
            className="flex-1"
          />
          <div className="flex gap-2">
            <Button type="button" size="sm" variant="outline" onClick={() => setSteps(String((Number(steps) || 0) + 1000))}>+1k</Button>
            <Button type="button" size="sm" variant="outline" onClick={() => setSteps(String((Number(steps) || 0) + 5000))}>+5k</Button>
          </div>
        </div>
      </Card>
      )}

      {(!fields || fields.includes('sleep')) && (
        <Card>
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary-fixed text-on-primary-fixed-variant">
              <Moon className="h-6 w-6" />
            </div>
            <h3 className="text-headline-md text-on-surface">Sleep (hours)</h3>
          </div>
          <div className="mt-3 flex flex-col gap-3 sm:flex-row sm:items-center">
            <Input
              type="number"
              step="0.25"
              min={0}
              max={24}
              value={sleep}
              onChange={(e) => setSleep(e.target.value)}
              placeholder="0.0"
              className="flex-1"
            />
            <input
              type="range"
              min={0}
              max={12}
              step={0.25}
              value={sleep || 0}
              onChange={(e) => setSleep(e.target.value)}
              className="h-2 w-full sm:w-48 accent-primary"
            />
          </div>
        </Card>
      )}

      {(!fields || fields.includes('water')) && (
        <Card>
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-tertiary-fixed text-on-tertiary-fixed-variant">
              <Droplet className="h-6 w-6" />
            </div>
            <h3 className="text-headline-md text-on-surface">Water (liters)</h3>
          </div>
          <div className="mt-3 flex flex-col gap-3 sm:flex-row sm:items-center">
            <Input
              type="number"
              step="0.1"
              min={0}
              max={10}
              value={water}
              onChange={(e) => setWater(e.target.value)}
              placeholder="0.0"
              className="flex-1"
            />
            <Button type="button" size="sm" variant="tertiary" onClick={addWaterGlass}>
              <Plus className="h-4 w-4" /> 250 ml glass
            </Button>
          </div>
        </Card>
      )}

      {(!fields || fields.includes('food')) && (
        <Card>
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-surface-container-high text-on-surface">
              <UtensilsCrossed className="h-6 w-6" />
            </div>
            <h3 className="text-headline-md text-on-surface">Food log</h3>
          </div>
          <div className="mt-3 flex flex-col gap-md">
          {MEALS.map((meal) => (
            <div key={meal}>
              <p className="mb-1.5 text-label-lg capitalize text-on-surface-variant">{meal}</p>
              <div className="flex flex-wrap items-center gap-2">
                {food[meal].map((item, i) => (
                  <span
                    key={`${item}-${i}`}
                    className="inline-flex items-center gap-1 rounded-full bg-surface-container px-3 py-1 text-body-sm text-on-surface"
                  >
                    {item}
                    <button type="button" onClick={() => removeFoodItem(meal, i)} aria-label="Remove">
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                ))}
                <input
                  className="h-9 min-w-[140px] flex-1 rounded-lg bg-surface-container-low px-3 text-body-sm outline-none focus:ring-2 focus:ring-primary"
                  placeholder="Add item & press enter"
                  value={drafts[meal]}
                  onChange={(e) => setDrafts((d) => ({ ...d, [meal]: e.target.value }))}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault()
                      addFoodItem(meal)
                    }
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      </Card>
      )}

      <Button type="submit" size="lg" loading={submitting}>{submitLabel}</Button>
    </form>
  )
}
