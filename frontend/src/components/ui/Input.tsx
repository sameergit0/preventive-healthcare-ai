import { forwardRef, type InputHTMLAttributes, type ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  hint?: string
  leftAdornment?: ReactNode
  rightAdornment?: ReactNode
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, hint, leftAdornment, rightAdornment, id, ...rest }, ref) => {
    const inputId = id ?? rest.name
    return (
      <div className="flex flex-col gap-1.5">
        {label && (
          <label htmlFor={inputId} className="text-label-lg text-on-surface-variant">
            {label}
          </label>
        )}
        <div
          className={cn(
            'flex h-14 items-center gap-2 rounded-lg bg-surface-container-low px-4 transition-shadow',
            'focus-within:ring-2 focus-within:ring-primary',
            error && 'ring-2 ring-error',
          )}
        >
          {leftAdornment && <span className="text-on-surface-variant">{leftAdornment}</span>}
          <input
            ref={ref}
            id={inputId}
            className={cn(
              'flex-1 bg-transparent text-body-md text-on-surface placeholder:text-on-surface-variant/60 outline-none',
              className,
            )}
            aria-invalid={!!error || undefined}
            {...rest}
          />
          {rightAdornment && <span className="text-on-surface-variant">{rightAdornment}</span>}
        </div>
        {(error || hint) && (
          <p className={cn('text-body-sm', error ? 'text-error' : 'text-on-surface-variant')}>
            {error ?? hint}
          </p>
        )}
      </div>
    )
  },
)
Input.displayName = 'Input'
