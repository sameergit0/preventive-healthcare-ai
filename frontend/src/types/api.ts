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

export interface ProfileGetResponse {
  message: string
  profile: Profile | null
}

export interface ProfilePhotoResponse {
  message: string
  image_url: string | null
}

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

// Analytics
export interface MetricSummary {
  average: number | null
  total: number | null
  max: number | null
  min: number | null
  days_recorded: number
  target: number | null
  achievement_rate: number | null
}

export interface HealthSummaryResponse {
  period_start: string
  period_end: string
  total_days: number
  active_days: number
  steps: MetricSummary
  sleep: MetricSummary
  water: MetricSummary
  activity: MetricSummary
  sedentary: MetricSummary
  sugar: MetricSummary
  fruits: MetricSummary
}

export type MetricType = 'steps' | 'sleep' | 'water' | 'activity' | 'sedentary' | 'sugar' | 'fruits'
export type Severity = 'good' | 'warning' | 'critical'
export type Priority = 'high' | 'medium' | 'low'

export interface Insight {
  type: MetricType
  message: string
  severity: Severity
}

export interface HealthInsightsResponse {
  overall_score: number
  insights: Insight[]
}

export interface MetricTrend {
  current_avg: number | null
  previous_avg: number | null
  change_percent: number | null
}

export interface HealthTrendsResponse {
  steps: MetricTrend
  sleep: MetricTrend
  water: MetricTrend
  activity: MetricTrend
  sedentary: MetricTrend
  sugar: MetricTrend
  fruits: MetricTrend
}

export interface Recommendation {
  type: MetricType
  message: string
  priority: Priority
}

export interface HealthRecommendationsResponse {
  recommendations: Recommendation[]
}

export interface HealthScorePoint {
  date: string
  score: number | null
}

export interface HealthScoreHistoryResponse {
  scores: HealthScorePoint[]
}

export interface TimezonesResponse {
  grouped: Record<string, string[]>
}

export interface ApiError {
  detail: string | Array<{ loc: string[]; msg: string; type: string }>
}
