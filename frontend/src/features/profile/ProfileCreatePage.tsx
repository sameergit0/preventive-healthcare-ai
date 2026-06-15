import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { toast } from 'sonner'
import { Card } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { Chip } from '@/components/ui/Chip'
import { Spinner } from '@/components/ui/Spinner'
import { GOALS, type Goal } from '@/types/api'
import { profileSchema, type ProfileForm } from '@/lib/validation'
import { useCreateProfile, useProfile } from './api'
import { PhotoPicker } from './PhotoPicker'
import { getErrorMessage } from '@/lib/api'
import { cn } from '@/lib/utils'
import { useGetLifestyle, useGetMedicalHistory } from '@/features/onboarding/api'
import { LifestyleModal } from '@/features/onboarding/LifestyleModal'
import { MedicalHistoryModal } from '@/features/onboarding/MedicalHistoryModal'
import { HealthMetricsModal } from '@/features/onboarding/HealthMetricsModal'

type OnboardingStep = 'profile' | 'lifestyle' | 'medical' | 'metrics' | 'done'

export function ProfileCreatePage() {
  const navigate = useNavigate()
  const { data: profileData, isLoading: profileLoading } = useProfile()
  const lifestyle = useGetLifestyle()
  const medical = useGetMedicalHistory()
  
  const create = useCreateProfile()
  const [file, setFile] = useState<File | null>(null)
  const [step, setStep] = useState<OnboardingStep>('profile')

  const loading = profileLoading || lifestyle.isLoading || medical.isLoading

  useEffect(() => {
    if (loading) return

    if (!profileData) {
      setStep('profile')
    } else if (!lifestyle.data) {
      setStep('lifestyle')
    } else if (!medical.data) {
      setStep('medical')
    } else {
      navigate('/dashboard', { replace: true })
    }
  }, [profileData, lifestyle.data, medical.data, loading, navigate])

  const {
    register,
    handleSubmit,
    control,
    formState: { errors },
  } = useForm<ProfileForm>({
    resolver: zodResolver(profileSchema),
    values: profileData ? {
      full_name: profileData.full_name,
      age: profileData.age,
      gender: profileData.gender,
      weight: profileData.weight,
      height: profileData.height,
      waist_cm: profileData.waist_cm ?? undefined,
      goal: profileData.goal,
    } : undefined,
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
      toast.success('Profile created!')
      setStep('lifestyle')
    } catch (e: unknown) {
      if (axios.isAxiosError(e) && e.response?.status === 409) {
        navigate('/profile/edit', { replace: true })
        return
      }
      toast.error(getErrorMessage(e))
    }
  })

  if (loading) {
    return (
      <div className="flex min-h-[400px] items-center justify-center">
        <Spinner />
      </div>
    )
  }

  const steps: { key: OnboardingStep; label: string }[] = [
    { key: 'profile', label: 'Basic Info' },
    { key: 'lifestyle', label: 'Lifestyle' },
    { key: 'medical', label: 'Medical' },
    { key: 'metrics', label: 'Targets' },
  ]

  const currentStepIdx = steps.findIndex((s) => s.key === step)

  // Handle step transitions
  const handleLifestyleComplete = () => {
    lifestyle.refetch()
    setStep('medical')
  }
  const handleMedicalComplete = () => {
    medical.refetch()
    setStep('metrics')
  }
  const handleMetricsComplete = () => {
    toast.success('Welcome to Vitality! Your dashboard is ready.')
    navigate('/dashboard', { replace: true })
  }

  return (
    <>
      <div className="mx-auto w-full max-w-2xl">
        {/* Step Indicator */}
        <div className="mb-8 flex items-center justify-between">
          {steps.map((s, i) => (
            <div key={s.key} className="flex flex-1 items-center last:flex-none">
              <div className="flex flex-col items-center gap-2">
                <div className={cn(
                  "flex h-10 w-10 items-center justify-center rounded-full text-label-lg font-bold transition-all shadow-level-1",
                  i <= currentStepIdx ? "bg-primary text-primary-on scale-110 shadow-primary/20" : "bg-surface-container-high text-on-surface-variant"
                )}>
                  {i < currentStepIdx ? '✓' : i + 1}
                </div>
                <span className={cn(
                  "text-label-sm font-semibold",
                  i <= currentStepIdx ? "text-on-surface" : "text-on-surface-variant"
                )}>
                  {s.label}
                </span>
              </div>
              {i < steps.length - 1 && (
                <div className={cn(
                  "mx-2 h-[2px] flex-1 transition-colors",
                  i < currentStepIdx ? "bg-primary" : "bg-surface-container-high"
                )} />
              )}
            </div>
          ))}
        </div>

        {step === 'profile' && (
          <>
            <h1 className="text-headline-xl text-on-surface">Set up your profile</h1>
            <p className="mt-2 text-body-md text-on-surface-variant">Tell us a little about yourself so we can personalize your insights.</p>
            <form onSubmit={onSubmit} className="mt-md">
          <Card className="flex flex-col gap-md">
            <PhotoPicker 
              value={file} 
              onChange={setFile} 
              existingUrl={profileData?.profile_image} 
            />
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
              Submit
            </Button>
          </Card>
            </form>
          </>
        )}

        {step !== 'profile' && step !== 'done' && (
          <div className="flex flex-col items-center justify-center py-xl text-center">
            <h1 className="text-headline-xl text-on-surface">Almost there...</h1>
            <p className="mt-2 text-body-md text-on-surface-variant">
              Complete these optional steps to unlock advanced health scoring.
            </p>
            <div className="mt-md">
              <Spinner />
            </div>
          </div>
        )}
      </div>

      {/* Onboarding Modals */}
      <LifestyleModal 
        open={step === 'lifestyle'} 
        onComplete={handleLifestyleComplete} 
        initialData={lifestyle.data} 
      />
      <MedicalHistoryModal 
        open={step === 'medical'} 
        onComplete={handleMedicalComplete} 
        initialData={medical.data} 
      />
      <HealthMetricsModal open={step === 'metrics'} onComplete={handleMetricsComplete} />
    </>
  )
}
