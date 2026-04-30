import { Minus, Plus } from 'lucide-react'
import { cn } from '@/lib/utils'

interface StepperProps {
  value: number
  onChange: (value: number) => void
  step?: number
  min?: number
  max?: number
  unit?: string
  className?: string
}

export function Stepper({ value, onChange, step = 1, min = 0, max = 1440, unit, className }: StepperProps) {
  const increment = () => onChange(Math.min(max, value + step))
  const decrement = () => onChange(Math.max(min, value - step))

  return (
    <div className={cn('flex items-center gap-3 rounded-xl bg-surface-container-low p-1', className)}>
      <button
        type="button"
        onClick={decrement}
        disabled={value <= min}
        className="flex h-10 w-10 items-center justify-center rounded-lg bg-surface-container-high text-on-surface transition-colors hover:bg-surface-container-highest disabled:opacity-30"
      >
        <Minus className="h-4 w-4" />
      </button>
      <div className="flex flex-1 flex-col items-center justify-center">
        <span className="text-headline-small font-bold text-on-surface">{value}</span>
        {unit && <span className="text-label-small text-on-surface-variant">{unit}</span>}
      </div>
      <button
        type="button"
        onClick={increment}
        disabled={value >= max}
        className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-primary-on transition-colors hover:bg-primary/90 disabled:opacity-30"
      >
        <Plus className="h-4 w-4" />
      </button>
    </div>
  )
}
