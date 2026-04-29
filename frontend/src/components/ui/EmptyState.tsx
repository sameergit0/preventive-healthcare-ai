import type { ReactNode } from 'react'
import { Card } from './Card'

export function EmptyState({ icon, title, description, action }: { icon?: ReactNode; title: string; description?: string; action?: ReactNode }) {
  return (
    <Card className="flex flex-col items-center gap-3 py-lg text-center">
      {icon && <div className="text-primary">{icon}</div>}
      <h3 className="text-headline-md text-on-surface">{title}</h3>
      {description && <p className="text-body-md text-on-surface-variant max-w-md">{description}</p>}
      {action}
    </Card>
  )
}
