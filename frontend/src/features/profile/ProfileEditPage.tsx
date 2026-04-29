import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { toast } from 'sonner'
import { Card } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { Chip } from '@/components/ui/Chip'
import { Spinner } from '@/components/ui/Spinner'
import { Modal } from '@/components/ui/Modal'
import { Avatar } from '@/components/ui/Avatar'
import { useDeletePhoto, useDeleteProfile, useProfile, useUpdatePhoto, useUpdateProfile } from './api'
import { GOALS, type Goal, type Profile } from '@/types/api'
import { profileSchema, type ProfileForm } from '@/lib/validation'
import { getErrorMessage } from '@/lib/api'
import { useDropzone } from 'react-dropzone'
import { cn } from '@/lib/utils'

export function ProfileEditPage() {
  const navigate = useNavigate()
  const { data, isLoading } = useProfile()
  const update = useUpdateProfile()
  const updatePhoto = useUpdatePhoto()
  const deletePhoto = useDeletePhoto()
  const deleteProfile = useDeleteProfile()
  const [confirmDelete, setConfirmDelete] = useState(false)

  const {
    register,
    handleSubmit,
    reset,
    control,
    formState: { errors, isDirty, dirtyFields },
  } = useForm<ProfileForm>({ resolver: zodResolver(profileSchema) })

  useEffect(() => {
    if (data?.profile) {
      reset({
        full_name: data.profile.full_name,
        age: data.profile.age,
        gender: data.profile.gender,
        weight: data.profile.weight,
        height: data.profile.height,
        waist_cm: data.profile.waist_cm ?? '',
        goal: data.profile.goal,
      })
    }
  }, [data?.profile, reset])

  const photoDz = useDropzone({
    accept: { 'image/jpeg': [], 'image/png': [] },
    maxFiles: 1,
    onDrop: async (files) => {
      if (!files[0]) return
      try {
        await updatePhoto.mutateAsync(files[0])
        toast.success('Photo updated')
      } catch (e) {
        toast.error(getErrorMessage(e))
      }
    },
  })

  const onSubmit = handleSubmit(async (values) => {
    // Build patch only from dirty fields to avoid sending unchanged data
    const patch: Record<string, unknown> = {}
    const allowedFields: (keyof ProfileForm)[] = ['full_name', 'age', 'gender', 'weight', 'height', 'waist_cm', 'goal']

    Object.keys(dirtyFields).forEach((k) => {
      const key = k as keyof ProfileForm
      if (!allowedFields.includes(key)) return

      const val = values[key]
      patch[key] = val === '' ? null : val
    })

    if (Object.keys(patch).length === 0) return

    try {
      // Cast to the expected mutation type since we've manually verified the fields
      await update.mutateAsync(patch as Partial<Profile>)
      toast.success('Profile updated')
    } catch (e) {
      console.error('Profile update failed:', e)
      toast.error(getErrorMessage(e))
    }
  })

  const onDeletePhoto = async () => {
    try {
      await deletePhoto.mutateAsync()
      toast.success('Photo removed')
    } catch (e) {
      toast.error(getErrorMessage(e))
    }
  }

  const onDeleteProfile = async () => {
    try {
      await deleteProfile.mutateAsync()
      toast.success('Profile deleted')
      navigate('/profile/create', { replace: true })
    } catch (e) {
      toast.error(getErrorMessage(e))
    } finally {
      setConfirmDelete(false)
    }
  }

  if (isLoading) {
    return <div className="flex justify-center py-lg"><Spinner /></div>
  }

  if (!data?.profile) {
    navigate('/profile/create', { replace: true })
    return null
  }

  return (
    <div className="mx-auto w-full max-w-2xl">
      <h1 className="text-headline-xl text-on-surface">Edit profile</h1>
      <form onSubmit={onSubmit} className="mt-md flex flex-col gap-md">
        <Card>
          <div className="flex flex-col items-center gap-3 sm:flex-row sm:items-center">
            <Avatar src={data.profile.profile_image} name={data.profile.full_name} size={80} />
            <div className="flex flex-col gap-2">
              <div {...photoDz.getRootProps()} className="cursor-pointer">
                <input {...photoDz.getInputProps()} />
                <Button type="button" variant="outline" size="sm" loading={updatePhoto.isPending}>
                  {data.profile.profile_image ? 'Replace photo' : 'Upload photo'}
                </Button>
              </div>
              {data.profile.profile_image && (
                <Button type="button" variant="ghost" size="sm" onClick={onDeletePhoto} loading={deletePhoto.isPending}>
                  Remove photo
                </Button>
              )}
            </div>
          </div>
          {data.profile.bmi && (
            <div className="mt-4 flex flex-wrap gap-md border-t border-surface-variant pt-4">
              <div className="flex flex-col">
                <span className="text-label-sm uppercase text-on-surface-variant">Current BMI</span>
                <span className="text-headline-md text-on-surface">{data.profile.bmi}</span>
              </div>
              <div className="flex flex-col">
                <span className="text-label-sm uppercase text-on-surface-variant">Category</span>
                <span className={cn(
                  "text-headline-md",
                  data.profile.bmi_category === 'Normal' ? "text-primary" : "text-error"
                )}>
                  {data.profile.bmi_category}
                </span>
              </div>
              {data.profile.waist_cm && (
                <div className="flex flex-col">
                  <span className="text-label-sm uppercase text-on-surface-variant">Waist</span>
                  <span className="text-headline-md text-on-surface">{data.profile.waist_cm} cm</span>
                </div>
              )}
            </div>
          )}
        </Card>
        <Card className="flex flex-col gap-md">
          <Input label="Full name" error={errors.full_name?.message} {...register('full_name')} />
          <div className="grid grid-cols-1 gap-md sm:grid-cols-2">
            <Input label="Age" type="number" error={errors.age?.message} {...register('age')} />
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
            <Input label="Weight (kg)" type="number" step="0.1" error={errors.weight?.message} {...register('weight')} />
            <Input label="Height (cm)" type="number" step="0.1" error={errors.height?.message} {...register('height')} />
          </div>
          <Input label="Waist (cm) - Optional" type="number" step="0.1" error={errors.waist_cm?.message} {...register('waist_cm')} />
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
              </div>
            )}
          />
          <Button type="submit" size="lg" disabled={!isDirty} loading={update.isPending}>
            Save changes
          </Button>
        </Card>
        <Card className="border border-error/30">
          <h3 className="text-headline-md text-error">Danger zone</h3>
          <p className="mt-1 text-body-sm text-on-surface-variant">Deleting your profile removes all personal info but keeps your account.</p>
          <Button type="button" variant="destructive" className="mt-3" onClick={() => setConfirmDelete(true)}>
            Delete profile
          </Button>
        </Card>
      </form>
      <Modal open={confirmDelete} onClose={() => setConfirmDelete(false)} title="Delete profile?">
        <p className="text-body-md text-on-surface-variant">This cannot be undone.</p>
        <div className="mt-md flex justify-end gap-2">
          <Button variant="ghost" onClick={() => setConfirmDelete(false)}>Cancel</Button>
          <Button variant="destructive" onClick={onDeleteProfile} loading={deleteProfile.isPending}>
            Yes, delete
          </Button>
        </div>
      </Modal>
    </div>
  )
}
