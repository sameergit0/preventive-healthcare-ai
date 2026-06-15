// Auth
export interface User {
  id: number
  email: string
  timezone: string
}

export interface SignupRequest {
  email: string
  password: string
  timezone: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface TokenResponse {
  message: string
  access_token: string
  token_type: 'bearer'
}

// Profile
export type Gender = 'M' | 'F'
export type Goal =
  | 'Weight Loss'
  | 'Weight Gain'
  | 'Muscle Building'
  | 'Maintain Fitness'
  | 'Improve Sleep'
  | 'Reduce Stress'

export const GOALS: Goal[] = [
  'Weight Loss',
  'Weight Gain',
  'Muscle Building',
  'Maintain Fitness',
  'Improve Sleep',
  'Reduce Stress',
]

export interface Profile {
  id: number
  full_name: string
  age: number
  gender: Gender
  weight: number
  height: number
  waist_cm: number | null
  goal: Goal
  profile_image: string | null
  bmi: number | null
  bmi_category: string | null
}

export type ProfileGetResponse = Profile

// Lifestyle
export type TobaccoType = 'never' | 'daily' | 'weekly' | 'occasionally' | 'former'
export type AlcoholFreq = 'never' | 'rarely' | 'sometimes' | 'often' | 'daily'

export const TOBACCO_OPTIONS: { value: TobaccoType; label: string }[] = [
  { value: 'never', label: 'Never' },
  { value: 'daily', label: 'Daily' },
  { value: 'weekly', label: 'Weekly' },
  { value: 'occasionally', label: 'Occasionally' },
  { value: 'former', label: 'Former' },
]

export const ALCOHOL_OPTIONS: { value: AlcoholFreq; label: string }[] = [
  { value: 'never', label: 'Never' },
  { value: 'rarely', label: 'Rarely' },
  { value: 'sometimes', label: 'Sometimes' },
  { value: 'often', label: 'Often' },
  { value: 'daily', label: 'Daily' },
]

export interface LifestyleCreate {
  tobacco_type?: TobaccoType | null
  passive_smoke?: boolean | null
  alcohol_freq?: AlcoholFreq | null
  alcohol_binge?: boolean | null
  stress_level?: number | null
  work_life_balance?: number | null
  screen_time_hours?: number | null
}

export interface LifestyleResponse extends LifestyleCreate {
  id?: number
}

// Medical History
export interface MedicalHistoryCreate {
  diabetes?: boolean | null
  bp?: boolean | null
  high_cholesterol?: boolean | null
  heart_disease?: boolean | null
  asthma?: boolean | null
}

export interface MedicalHistoryResponse extends MedicalHistoryCreate {
  id?: number
}

export const MEDICAL_CONDITIONS: { key: keyof MedicalHistoryCreate; label: string; description: string }[] = [
  { key: 'diabetes', label: 'Diabetes', description: 'Type 1 or Type 2 diabetes' },
  { key: 'bp', label: 'High Blood Pressure', description: 'Hypertension' },
  { key: 'high_cholesterol', label: 'High Cholesterol', description: 'Elevated LDL levels' },
  { key: 'heart_disease', label: 'Heart Disease', description: 'Any cardiovascular condition' },
  { key: 'asthma', label: 'Asthma', description: 'Respiratory condition' },
]

// Health logs
export type Meal = 'breakfast' | 'lunch' | 'dinner'

export interface FoodItem {
  meal: Meal
  items: string[]
}

export interface DailyHealthLog {
  id: number
  log_date: string
  steps: number | null
  sleep_hours: number | null
  water_intake: number | null
  food_log: FoodItem[]
  sleep_quality: 'poor' | 'average' | 'good' | 'excellent' | null
  activity_minutes: number | null
  sedentary_minutes: number | null
  nutrition_sugar: number | null
  nutrition_fruits: number | null
  created_at: string
}

export interface DailyHealthLogCreate {
  steps?: number
  sleep_hours?: number
  water_intake?: number
  food_log?: FoodItem[]
  sleep_quality?: 'poor' | 'average' | 'good' | 'excellent'
  activity_minutes?: number
  sedentary_minutes?: number
  nutrition_sugar?: number
  nutrition_fruits?: number
}

export interface AllLogsResponse {
  message: string
  logs: DailyHealthLog[]
  total: number
}

// Analytics — matches backend schemas exactly

// MetricSummary — matches backend app.schemas.analytics.MetricSummary
export interface MetricSummary {
  avg: number
  min: number
  max: number
  total: number
  days_recorded: number
  target: number
  achievement_rate: number
}

// CategoricalMetricSummary — matches backend
export interface CategoricalMetricSummary {
  most_frequent: string | null
  recorded_days: number
}

// OverallSummaryResponse — matches backend
export interface OverallSummaryResponse {
  message: string
  steps: MetricSummary
  sleep: MetricSummary
  water: MetricSummary
  activity: MetricSummary
  sedentary: MetricSummary
  sugar: MetricSummary
  fruits: MetricSummary
  sleep_quality: CategoricalMetricSummary
}

// HealthInsight — matches backend
export interface HealthInsight {
  category: string
  message: string
  priority: string
  trend: string | null
}

// InsightsResponse — matches backend
export interface InsightsResponse {
  health_score: number
  risk_level: string
  insights: HealthInsight[]
  summary_message: string
}

// TrendDataPoint — matches backend
export interface TrendDataPoint {
  log_date: string
  health_score: number
}

// TrendsResponse — matches backend
export interface TrendsResponse {
  message: string
  data: TrendDataPoint[]
}

// Recommendation — matches backend
export interface Recommendation {
  task: string
  benefit: string
  priority: string
  category: string
}

// RecommendationsResponse — matches backend
export interface RecommendationsResponse {
  message: string
  recommendations: Recommendation[]
}

// HealthStatusResponse — matches backend
export interface HealthStatusResponse {
  health_score: number
  risk_level: string
  summary_message: string
}

export type MetricKey = 'steps' | 'sleep' | 'water' | 'activity' | 'sedentary' | 'sugar' | 'fruits'

export interface TimezonesResponse {
  grouped: Record<string, string[]>
}

export interface ApiError {
  detail: string | Array<{ loc: string[]; msg: string; type: string }>
}
