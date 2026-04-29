import { useEffect, type ReactNode } from 'react'
import { X } from 'lucide-react'
import { cn } from '@/lib/utils'

export function Modal({ open, onClose, title, children, className }: { open: boolean; onClose: () => void; title?: string; children: ReactNode; className?: string }) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose()
    if (open) document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [open, onClose])

  if (!open) return null
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" role="dialog" aria-modal="true">
      <div className="absolute inset-0 bg-on-surface/50" onClick={onClose} />
      <div className={cn('relative z-10 flex max-h-[90vh] w-full max-w-lg flex-col rounded-xl bg-surface-container-lowest p-md shadow-level-2', className)}>
        <div className="flex shrink-0 items-start justify-between gap-4">
          {title && <h2 className="text-headline-md text-on-surface">{title}</h2>}
          <button onClick={onClose} className="ml-auto rounded-full p-1 hover:bg-surface-container" aria-label="Close">
            <X className="h-5 w-5" />
          </button>
        </div>
        <div className="scrollbar-thin mt-4 overflow-y-auto pr-2">
          {children}
        </div>
      </div>
    </div>
  )
}
