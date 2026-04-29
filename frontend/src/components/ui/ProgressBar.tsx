import { cn } from '@/lib/utils'

export function ProgressBar({ value, className, fillClassName = 'bg-tertiary' }: { value: number; className?: string; fillClassName?: string }) {
  const clamped = Math.max(0, Math.min(100, value))
  return (
    <div className={cn('h-3 w-full overflow-hidden rounded-full bg-surface-container-high', className)}>
      <div
        className={cn('h-full rounded-full transition-all', fillClassName)}
        style={{ width: `${clamped}%` }}
      />
    </div>
  )
}
