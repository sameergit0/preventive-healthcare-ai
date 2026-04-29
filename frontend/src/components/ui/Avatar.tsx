import { useState } from 'react'
import { cn } from '@/lib/utils'
import { getInitials } from '@/lib/utils'

export function Avatar({ src, name, size = 40, className }: { src?: string | null; name?: string; size?: number; className?: string }) {
  const [errored, setErrored] = useState(false)
  const initials = name ? getInitials(name) : '?'
  return (
    <div
      className={cn('inline-flex items-center justify-center overflow-hidden rounded-full bg-primary-container text-primary-on font-semibold', className)}
      style={{ width: size, height: size, fontSize: size * 0.4 }}
    >
      {src && !errored ? (
        <img src={src} alt={name ?? 'avatar'} className="h-full w-full object-cover" onError={() => setErrored(true)} />
      ) : (
        <span>{initials}</span>
      )}
    </div>
  )
}
