import { forwardRef, type SelectHTMLAttributes } from 'react'
import { ChevronDown } from 'lucide-react'
import { cn } from '@/lib/utils'

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string
  error?: string
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, label, error, id, children, ...rest }, ref) => {
    const selectId = id ?? rest.name
    return (
      <div className="flex flex-col gap-1.5">
        {label && (
          <label htmlFor={selectId} className="text-label-lg text-on-surface-variant">
            {label}
          </label>
        )}
        <div
          className={cn(
            'relative flex h-14 items-center rounded-lg bg-surface-container-low px-4',
            'focus-within:ring-2 focus-within:ring-primary',
            error && 'ring-2 ring-error',
          )}
        >
          <select
            ref={ref}
            id={selectId}
            className={cn(
              'w-full appearance-none bg-transparent text-body-md text-on-surface outline-none',
              className,
            )}
            {...rest}
          >
            {children}
          </select>
          <ChevronDown className="pointer-events-none absolute right-4 h-5 w-5 text-on-surface-variant" />
        </div>
        {error && <p className="text-body-sm text-error">{error}</p>}
      </div>
    )
  },
)
Select.displayName = 'Select'
