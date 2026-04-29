import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Eye, EyeOff, Lock, Mail } from 'lucide-react'
import { useMemo, useState } from 'react'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { Select } from '@/components/ui/Select'
import { useLogin, useSignup, useTimezones } from './api'
import { signupSchema, type SignupForm } from '@/lib/validation'
import { getErrorMessage } from '@/lib/api'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'

const browserTz = (() => {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone
  } catch {
    return 'UTC'
  }
})()

export function SignupPage() {
  const navigate = useNavigate()
  const signup = useSignup()
  const login = useLogin()
  const tzQuery = useTimezones()
  const [showPwd, setShowPwd] = useState(false)
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<SignupForm>({
    resolver: zodResolver(signupSchema),
    defaultValues: { timezone: browserTz },
  })

  const password = watch('password') ?? ''
  const rules = useMemo(
    () => [
      { ok: password.length >= 8 && password.length <= 64, label: '8–64 characters' },
      { ok: /[A-Z]/.test(password), label: 'Uppercase letter' },
      { ok: /[a-z]/.test(password), label: 'Lowercase letter' },
      { ok: /\d/.test(password), label: 'Digit' },
      { ok: /[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(password), label: 'Special character' },
    ],
    [password],
  )

  const onSubmit = handleSubmit(async (values) => {
    try {
      await signup.mutateAsync(values)
      await login.mutateAsync({ email: values.email, password: values.password })
      navigate('/profile/create', { replace: true })
    } catch (e) {
      toast.error(getErrorMessage(e))
    }
  })

  const tzOptions = useMemo(() => {
    const grouped = tzQuery.data?.grouped ?? {}
    return Object.entries(grouped).sort(([a], [b]) => a.localeCompare(b))
  }, [tzQuery.data])

  return (
    <div className="flex flex-1 flex-col gap-md">
      <div>
        <h1 className="text-headline-xl text-on-surface">Create your account</h1>
        <p className="mt-2 text-body-md text-on-surface-variant">Start your preventive healthcare journey.</p>
      </div>
      <form onSubmit={onSubmit} className="flex flex-col gap-md">
        <Input
          label="Email"
          type="email"
          autoComplete="email"
          leftAdornment={<Mail className="h-5 w-5" />}
          error={errors.email?.message}
          {...register('email')}
        />
        <div>
          <Input
            label="Password"
            type={showPwd ? 'text' : 'password'}
            autoComplete="new-password"
            leftAdornment={<Lock className="h-5 w-5" />}
            rightAdornment={
              <button type="button" onClick={() => setShowPwd((v) => !v)} aria-label="Toggle password">
                {showPwd ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
              </button>
            }
            error={errors.password?.message}
            {...register('password')}
          />
          <ul className="mt-2 grid grid-cols-2 gap-1">
            {rules.map((r) => (
              <li
                key={r.label}
                className={cn('text-body-sm', r.ok ? 'text-tertiary' : 'text-on-surface-variant')}
              >
                {r.ok ? '✓' : '○'} {r.label}
              </li>
            ))}
          </ul>
        </div>
        <Select label="Timezone" error={errors.timezone?.message} {...register('timezone')}>
          {tzOptions.map(([region, zones]) => (
            <optgroup key={region} label={region}>
              {zones.map((z) => (
                <option key={z} value={z}>
                  {z}
                </option>
              ))}
            </optgroup>
          ))}
        </Select>
        <Button type="submit" size="lg" loading={signup.isPending || login.isPending}>
          Sign up
        </Button>
      </form>
      <p className="text-center text-body-md text-on-surface-variant">
        Already have an account?{' '}
        <Link to="/login" className="font-semibold text-primary hover:underline">
          Log in
        </Link>
      </p>
    </div>
  )
}
