import type { ButtonHTMLAttributes, ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface ChipProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  selected?: boolean
  icon?: ReactNode
}

export function Chip({ className, selected, icon, children, ...rest }: ChipProps) {
  return (
    <button
      type="button"
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full px-4 py-2 text-body-sm font-medium transition-colors',
        selected
          ? 'bg-primary text-primary-on'
          : 'bg-surface-container text-on-surface hover:bg-surface-container-high',
        className,
      )}
      {...rest}
    >
      {icon}
      {children}
    </button>
  )
}
