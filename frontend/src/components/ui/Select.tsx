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
            'group relative flex h-14 items-center rounded-lg bg-surface-container-low transition-all duration-200 hover:bg-surface-container',
            'focus-within:ring-2 focus-within:ring-primary',
            error && 'ring-2 ring-error',
          )}
        >
          <select
            ref={ref}
            id={selectId}
            className={cn(
              'h-full w-full appearance-none bg-transparent px-4 pr-10 text-body-md text-on-surface outline-none cursor-pointer',
              className,
            )}
            {...rest}
          >
            {children}
          </select>
          <ChevronDown className="pointer-events-none absolute right-4 h-5 w-5 text-on-surface-variant transition-transform duration-200 group-focus-within:rotate-180" />
        </div>
        {error && <p className="text-body-sm text-error">{error}</p>}
      </div>
    )
  },
)
Select.displayName = 'Select'
