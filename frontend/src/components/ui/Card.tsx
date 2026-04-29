import { forwardRef, type HTMLAttributes } from 'react'
import { cn } from '@/lib/utils'

export const Card = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...rest }, ref) => (
    <div
      ref={ref}
      className={cn('rounded-xl bg-surface-container-lowest p-md shadow-level-1', className)}
      {...rest}
    />
  ),
)
Card.displayName = 'Card'
