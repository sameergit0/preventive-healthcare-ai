import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Eye, EyeOff, Mail, Lock } from 'lucide-react'
import { useState } from 'react'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { useLogin } from './api'
import { loginSchema, type LoginForm } from '@/lib/validation'
import { api, getErrorMessage } from '@/lib/api'
import { toast } from 'sonner'
import type { ProfileGetResponse } from '@/types/api'

export function LoginPage() {
  const navigate = useNavigate()
  const login = useLogin()
  const [showPwd, setShowPwd] = useState(false)
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>({ resolver: zodResolver(loginSchema) })

  const onSubmit = handleSubmit(async (values) => {
    try {
      await login.mutateAsync(values)
      const { data } = await api.get<ProfileGetResponse>('/api/v1/profile/')
      navigate(data.profile === null ? '/profile/create' : '/dashboard', { replace: true })
    } catch (e) {
      toast.error(getErrorMessage(e))
    }
  })

  return (
    <div className="flex flex-1 flex-col gap-md">
      <div>
        <h1 className="text-headline-xl text-on-surface">Welcome back</h1>
        <p className="mt-2 text-body-md text-on-surface-variant">Log in to continue tracking your wellness.</p>
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
        <Input
          label="Password"
          type={showPwd ? 'text' : 'password'}
          autoComplete="current-password"
          leftAdornment={<Lock className="h-5 w-5" />}
          rightAdornment={
            <button type="button" onClick={() => setShowPwd((v) => !v)} aria-label="Toggle password">
              {showPwd ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
            </button>
          }
          error={errors.password?.message}
          {...register('password')}
        />
        <Button type="submit" size="lg" loading={login.isPending}>
          Log in
        </Button>
      </form>
      <p className="text-center text-body-md text-on-surface-variant">
        New here?{' '}
        <Link to="/signup" className="font-semibold text-primary hover:underline">
          Create an account
        </Link>
      </p>
    </div>
  )
}
