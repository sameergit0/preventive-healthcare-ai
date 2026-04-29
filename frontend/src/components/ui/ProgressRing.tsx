import { cn } from '@/lib/utils'

interface ProgressRingProps {
  value: number // 0-100
  size?: number
  stroke?: number
  className?: string
  trackClassName?: string
  fillClassName?: string
  children?: React.ReactNode
}

export function ProgressRing({
  value,
  size = 80,
  stroke = 8,
  className,
  trackClassName = 'text-surface-container-high',
  fillClassName = 'text-tertiary',
  children,
}: ProgressRingProps) {
  const clamped = Math.max(0, Math.min(100, value))
  const r = (size - stroke) / 2
  const c = 2 * Math.PI * r
  const offset = c - (clamped / 100) * c
  return (
    <div className={cn('relative inline-flex items-center justify-center', className)} style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} strokeWidth={stroke} className={trackClassName} stroke="currentColor" fill="none" />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          strokeWidth={stroke}
          className={fillClassName}
          stroke="currentColor"
          fill="none"
          strokeLinecap="round"
          strokeDasharray={c}
          strokeDashoffset={offset}
          style={{ transition: 'stroke-dashoffset 0.4s ease' }}
        />
      </svg>
      {children !== undefined && (
        <div className="absolute inset-0 flex items-center justify-center">{children}</div>
      )}
    </div>
  )
}
