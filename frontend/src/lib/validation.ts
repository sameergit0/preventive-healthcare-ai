import { z } from 'zod'
import { GOALS } from '@/types/api'

const passwordRegex =
  /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*()_+\-=[\]{}|;:,.<>?]).{8,64}$/

export const passwordSchema = z
  .string()
  .min(8, 'At least 8 characters')
  .max(64, 'At most 64 characters')
  .regex(passwordRegex, 'Must include upper, lower, digit and special character')

export const emailSchema = z.string().email('Invalid email').transform((s) => s.toLowerCase())

export const signupSchema = z.object({
  email: emailSchema,
  password: passwordSchema,
  timezone: z.string().min(1, 'Timezone is required'),
})

export const loginSchema = z.object({
  email: emailSchema,
  password: z.string().min(1, 'Password is required'),
})

export const profileSchema = z.object({
  full_name: z
    .string()
    .min(3, 'At least 3 characters')
    .max(100, 'At most 100 characters')
    .regex(/^[a-zA-Z\s.'-]+$/, 'Only letters, spaces, . \' -')
    .refine((s) => s.trim().includes(' '), 'Enter first and last name'),
  age: z.coerce.number().int().min(1, 'Age must be > 0').max(119, 'Age must be < 120'),
  gender: z.enum(['M', 'F']),
  weight: z.coerce.number().min(30.01, 'Weight must be > 30').max(299.99, 'Weight must be < 300'),
  height: z.coerce.number().min(50.01, 'Height must be > 50').max(249.99, 'Height must be < 250'),
  waist_cm: z.coerce.number().min(30.01, 'Min 30cm').max(199.99, 'Max 200cm').optional().nullable().or(z.literal('')),
  goal: z.enum(GOALS as [string, ...string[]]),
})

export const profilePatchSchema = profileSchema.partial().refine(
  (v) => Object.values(v).some((x) => x !== undefined && x !== ''),
  { message: 'Provide at least one field' },
)

export const dailyLogSchema = z
  .object({
    steps: z.coerce.number().int().min(0).max(100000).optional(),
    sleep_hours: z.coerce.number().min(0).max(24).optional(),
    water_intake: z.coerce.number().min(0).max(10).optional(),
    food_log: z
      .array(
        z.object({
          meal: z.enum(['breakfast', 'lunch', 'dinner']),
          items: z.array(z.string().min(1)).min(1),
        }),
      )
      .optional(),
  })
  .refine(
    (v) =>
      v.steps !== undefined ||
      v.sleep_hours !== undefined ||
      v.water_intake !== undefined ||
      (v.food_log && v.food_log.length > 0),
    { message: 'Provide at least one metric' },
  )

export type SignupForm = z.input<typeof signupSchema>
export type LoginForm = z.input<typeof loginSchema>
export type ProfileForm = z.input<typeof profileSchema>
export type ProfileFormOutput = z.output<typeof profileSchema>
