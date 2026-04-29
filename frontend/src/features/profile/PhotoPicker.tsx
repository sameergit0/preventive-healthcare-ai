import { useDropzone } from 'react-dropzone'
import { Camera, X } from 'lucide-react'
import { useEffect, useState } from 'react'
import { cn } from '@/lib/utils'

const MAX_BYTES = 5 * 1024 * 1024

export function PhotoPicker({
  value,
  onChange,
  existingUrl,
}: {
  value: File | null
  onChange: (f: File | null) => void
  existingUrl?: string | null
}) {
  const [preview, setPreview] = useState<string | null>(null)

  useEffect(() => {
    if (!value) {
      setPreview(null)
      return
    }
    const url = URL.createObjectURL(value)
    setPreview(url)
    return () => URL.revokeObjectURL(url)
  }, [value])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { 'image/jpeg': [], 'image/png': [] },
    maxFiles: 1,
    maxSize: MAX_BYTES,
    onDrop: (files) => files[0] && onChange(files[0]),
  })

  const display = preview ?? existingUrl ?? null

  return (
    <div className="flex flex-col items-center gap-3">
      <div
        {...getRootProps()}
        className={cn(
          'relative flex h-32 w-32 cursor-pointer items-center justify-center overflow-hidden rounded-full bg-surface-container-low ring-2 ring-transparent transition',
          isDragActive && 'ring-primary',
        )}
      >
        <input {...getInputProps()} />
        {display ? (
          <img src={display} alt="" className="h-full w-full object-cover" />
        ) : (
          <Camera className="h-10 w-10 text-on-surface-variant" />
        )}
      </div>
      {value && (
        <button
          type="button"
          onClick={() => onChange(null)}
          className="inline-flex items-center gap-1 text-body-sm text-error hover:underline"
        >
          <X className="h-3 w-3" /> Remove
        </button>
      )}
      <p className="text-body-sm text-on-surface-variant">JPG or PNG, ≤ 5 MB</p>
    </div>
  )
}
