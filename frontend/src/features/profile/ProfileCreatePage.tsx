import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'
import { toast } from 'sonner'
import { Card } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { Chip } from '@/components/ui/Chip'
import { GOALS, type Goal } from '@/types/api'
import { profileSchema, type ProfileForm } from '@/lib/validation'
import { useCreateProfile } from './api'
import { PhotoPicker } from './PhotoPicker'
import { getErrorMessage } from '@/lib/api'

export function ProfileCreatePage() {
  const navigate = useNavigate()
  const create = useCreateProfile()
  const [file, setFile] = useState<File | null>(null)

  const {
    register,
    handleSubmit,
    control,
    formState: { errors },
  } = useForm<ProfileForm>({
    resolver: zodResolver(profileSchema),
    defaultValues: { gender: 'M', goal: 'Maintain Fitness' },
  })

  const onSubmit = handleSubmit(async (values) => {
    try {
      const fd = new FormData()
      Object.entries(values).forEach(([k, v]) => {
        const val = v === '' ? null : v
        if (val !== null) fd.append(k, String(val))
      })
      if (file) fd.append('file', file)
      await create.mutateAsync(fd)
      toast.success('Profile created')
      navigate('/dashboard', { replace: true })
    } catch (e: unknown) {
      if (axios.isAxiosError(e) && e.response?.status === 409) {
        navigate('/profile/edit', { replace: true })
        return
      }
      toast.error(getErrorMessage(e))
    }
  })

  return (
    <div className="mx-auto w-full max-w-2xl">
      <h1 className="text-headline-xl text-on-surface">Set up your profile</h1>
      <p className="mt-2 text-body-md text-on-surface-variant">Tell us a little about yourself so we can personalize your insights.</p>
      <form onSubmit={onSubmit} className="mt-md">
        <Card className="flex flex-col gap-md">
          <PhotoPicker value={file} onChange={setFile} />
          <Input label="Full name" placeholder="John Doe" error={errors.full_name?.message} {...register('full_name')} />
          <div className="grid grid-cols-1 gap-md sm:grid-cols-2">
            <Input label="Age" type="number" min={1} max={119} error={errors.age?.message} {...register('age')} />
            <Controller
              control={control}
              name="gender"
              render={({ field }) => (
                <div className="flex flex-col gap-1.5">
                  <span className="text-label-lg text-on-surface-variant">Gender</span>
                  <div className="flex gap-2">
                    <Chip selected={field.value === 'M'} onClick={() => field.onChange('M')}>Male</Chip>
                    <Chip selected={field.value === 'F'} onClick={() => field.onChange('F')}>Female</Chip>
                  </div>
                </div>
              )}
            />
          </div>
          <div className="grid grid-cols-1 gap-md sm:grid-cols-2">
            <Input label="Weight (kg)" type="number" step="0.1" min={31} max={299} error={errors.weight?.message} {...register('weight')} />
            <Input label="Height (cm)" type="number" step="0.1" min={51} max={249} error={errors.height?.message} {...register('height')} />
          </div>
          <Input label="Waist (cm) - Optional" type="number" step="0.1" placeholder="Optional" error={errors.waist_cm?.message} {...register('waist_cm')} />
          <Controller
            control={control}
            name="goal"
            render={({ field }) => (
              <div className="flex flex-col gap-1.5">
                <span className="text-label-lg text-on-surface-variant">Goal</span>
                <div className="flex flex-wrap gap-2">
                  {GOALS.map((g) => (
                    <Chip key={g} selected={field.value === g} onClick={() => field.onChange(g as Goal)}>
                      {g}
                    </Chip>
                  ))}
                </div>
                {errors.goal && <p className="text-body-sm text-error">{errors.goal.message}</p>}
              </div>
            )}
          />
          <Button type="submit" size="lg" loading={create.isPending}>
            Save profile
          </Button>
        </Card>
      </form>
    </div>
  )
}
