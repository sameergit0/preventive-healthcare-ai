# Preventive Healthcare AI - Frontend Development Guide

## Overview

This document provides comprehensive guidance for building a production‑grade frontend for the **Preventive Healthcare AI** platform. The backend is a FastAPI‑based RESTful API that handles user authentication, profile management, daily health logging, and advanced analytics.

The frontend should implement the following user journey:

1. **Home page** – Login / Signup
2. **Post‑login** – Profile creation/editing (automatically opened after successful login)
3. **Dashboard** – Display user profile data, log data, logging functionality, and analytics metrics

---

## Backend API Summary

### Base URL
```
http://localhost:8000
```

### CORS
The backend is configured to accept requests from `http://localhost:5173` and `http://localhost:5174` (typical Vite dev servers). Ensure your frontend runs on one of these origins.

### Authentication
JWT (Bearer token) authentication. After login, the frontend must store the token and include it in the `Authorization` header for all protected endpoints.

```
Authorization: Bearer <access_token>
```

---

## API Endpoints Reference

### Authentication

#### `POST /api/v1/auth/signup`
Register a new user.

**Request body:**
```json
{
  "email": "user@example.com",
  "password": "StrongP@ssword123",
  "timezone": "Asia/Kolkata"
}
```

**Response:**
```json
{
  "message": "User created successfully"
}
```

#### `POST /api/v1/auth/login`
Authenticate and receive a token.

**Request body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

**Response:**
```json
{
  "message": "User logged in successfully",
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

#### `GET /api/v1/auth/me`
Get current user details (requires authentication).

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "timezone": "Asia/Kolkata"
}
```

---

### Profile Management

#### `POST /api/v1/profile/`
Create a profile for the authenticated user (multipart/form‑data).

**Form fields:**
- `full_name` (string)
- `age` (integer, 1‑119)
- `gender` (string, "M" or "F")
- `weight` (float, kg)
- `height` (float, cm)
- `goal` (string, one of: "Weight Loss", "Weight Gain", "Muscle Building", "Maintain Fitness", "Improve Sleep", "Reduce Stress")
- `file` (optional, image file)

**Response:**
```json
{
  "id": 1,
  "full_name": "John Doe",
  "age": 28,
  "gender": "M",
  "weight": 72.5,
  "height": 175.0,
  "goal": "Muscle Building",
  "profile_image": "http://localhost:8000/uploads/profile_1.jpg"
}
```

#### `GET /api/v1/profile/`
Get the current user’s profile.

**Response:**
```json
{
  "message": "Profile fetched successfully",
  "profile": {
    "id": 1,
    "full_name": "John Doe",
    "age": 28,
    "gender": "M",
    "weight": 72.5,
    "height": 175.0,
    "goal": "Muscle Building",
    "profile_image": "http://localhost:8000/uploads/profile_1.jpg"
  }
}
```

If no profile exists:
```json
{
  "message": "Profile not found",
  "profile": null
}
```

#### `PATCH /api/v1/profile/`
Update profile fields (partial update).

**Request body (any subset of fields):**
```json
{
  "full_name": "John Smith",
  "age": 29,
  "weight": 73.0
}
```

**Response:** Updated profile object.

#### `DELETE /api/v1/profile/`
Delete the user’s profile (and associated image).

**Response:** 204 No Content.

#### Photo‑specific endpoints
- `PUT /api/v1/profile/photo` – Upload/update profile photo
- `GET /api/v1/profile/photo` – Get photo URL
- `DELETE /api/v1/profile/photo` – Delete photo

---

### Daily Health Logs

#### `POST /api/v1/metrics/daily-logs`
Create or update today’s health log (upsert). At least one metric must be provided.

**Request body:**
```json
{
  "steps": 8000,
  "sleep_hours": 7.5,
  "water_intake": 2.5,
  "food_log": [
    {
      "meal": "breakfast",
      "items": ["poha", "tea"]
    },
    {
      "meal": "lunch",
      "items": ["roti", "dal", "rice"]
    }
  ]
}
```

**Response:** The created/updated log.

#### `GET /api/v1/metrics/daily-logs`
Get health logs with flexible filtering.

**Query parameters:**
- `request_type` – "today", "all", or "range"
- `start_date`, `end_date` – required for "range"
- `page`, `limit` – for pagination

**Response:**
```json
{
  "message": "Successfully fetched 5 logs",
  "logs": [
    {
      "id": 1,
      "log_date": "2026-04-27",
      "steps": 8000,
      "sleep_hours": 7.5,
      "water_intake": 2.5,
      "food_log": [...],
      "created_at": "2026-04-27T12:00:00Z"
    }
  ],
  "total": 5
}
```

#### `PATCH /api/v1/metrics/daily-logs/{log_id}`
Update specific fields of a log.

#### `DELETE /api/v1/metrics/daily-logs/today`
Delete today’s log.

#### `DELETE /api/v1/metrics/daily-logs/{log_id}`
Delete a specific log.

---

### Analytics

All analytics endpoints require `start_date` and `end_date` query parameters (YYYY‑MM‑DD). The maximum range is 90 days.

#### `GET /api/v1/analytics/summary`
Get aggregated health summary.

**Response:**
```json
{
  "period_start": "2026-04-01",
  "period_end": "2026-04-30",
  "total_days": 30,
  "active_days": 25,
  "steps": {
    "average": 8450.5,
    "total": 253515,
    "max": 15000,
    "min": 2000,
    "days_recorded": 25,
    "target": 10000,
    "achievement_rate": 60.0
  },
  "sleep": { ... },
  "water": { ... }
}
```

#### `GET /api/v1/analytics/insights`
Get health insights with severity ratings.

**Response:**
```json
{
  "overall_score": 78,
  "insights": [
    {
      "type": "steps",
      "message": "You met your step goal on 60% of days. Try to increase daily consistency.",
      "severity": "warning"
    }
  ]
}
```

#### `GET /api/v1/analytics/trends`
Compare current period with previous period.

**Response:**
```json
{
  "steps": {
    "current_avg": 8450.5,
    "previous_avg": 7200.0,
    "change_percent": 17.4
  },
  "sleep": { ... },
  "water": { ... }
}
```

#### `GET /api/v1/analytics/recommendations`
Get personalized recommendations.

**Response:**
```json
{
  "recommendations": [
    {
      "type": "steps",
      "message": "Aim for a 10‑minute walk after each meal to boost daily steps.",
      "priority": "medium"
    }
  ]
}
```

#### `GET /api/v1/analytics/score-history`
Get daily health scores over a period.

**Response:**
```json
{
  "scores": [
    {
      "date": "2026-04-01",
      "score": 72
    },
    ...
  ]
}
```

---

## Data Models

### User
```typescript
interface User {
  id: number;
  email: string;
  timezone: string;
}
```

### Profile
```typescript
interface Profile {
  id: number;
  full_name: string;
  age: number;
  gender: 'M' | 'F';
  weight: number;
  height: number;
  goal: 'Weight Loss' | 'Weight Gain' | 'Muscle Building' | 'Maintain Fitness' | 'Improve Sleep' | 'Reduce Stress';
  profile_image?: string;
}
```

### Health Log
```typescript
interface FoodItem {
  meal: 'breakfast' | 'lunch' | 'dinner';
  items: string[];
}

interface DailyHealthLog {
  id: number;
  log_date: string; // YYYY-MM-DD
  steps?: number;
  sleep_hours?: number;
  water_intake?: number;
  food_log: FoodItem[];
  created_at: string; // ISO datetime
}
```

### Analytics
See the schema definitions in `app/schemas/analytics.py` for detailed structures.

---

## Frontend Architecture Recommendations

### Technology Stack
- **Framework**: React 18+ with TypeScript (or Vue 3 / SvelteKit)
- **Build tool**: Vite (fast, supports hot reload)
- **State management**: TanStack Query (React Query) for server state, Zustand or Context for client state
- **HTTP client**: Axios or fetch with interceptors for token injection
- **Routing**: React Router DOM (or equivalent)
- **UI library**: Tailwind CSS + Headless UI / Radix UI for accessible components
- **Charts**: Recharts or Chart.js for analytics visualizations
- **Form handling**: React Hook Form with Zod validation
- **Notifications**: Sonner or React Hot Toast

### Project Structure
```
src/
├── api/
│   ├── client.ts          # Axios instance with interceptors
│   ├── auth.ts            # Authentication API calls
│   ├── profile.ts
│   ├── metrics.ts
│   └── analytics.ts
├── components/
│   ├── layout/
│   │   ├── Header.tsx
│   │   └── Sidebar.tsx
│   ├── auth/
│   │   ├── LoginForm.tsx
│   │   └── SignupForm.tsx
│   ├── profile/
│   │   ├── ProfileForm.tsx
│   │   └── ProfilePhotoUpload.tsx
│   ├── dashboard/
│   │   ├── DailyLogForm.tsx
│   │   ├── MetricsCard.tsx
│   │   └── Charts/
│   └── ui/                # Reusable UI primitives
├── pages/
│   ├── HomePage.tsx       # Login/Signup
│   ├── DashboardPage.tsx
│   └── ProfilePage.tsx
├── stores/
│   ├── auth.store.ts      # Authentication state
│   └── user.store.ts      # User/profile state
├── hooks/
│   ├── useAuth.ts
│   └── useHealthLogs.ts
├── utils/
│   ├── validation.ts
│   └── date.ts
└── App.tsx
```

### Authentication Flow Implementation

1. **Login/Signup page** – Collect credentials, call API, store token in secure storage (e.g., `localStorage` or `sessionStorage`).
2. **Token persistence** – Use an axios interceptor to attach the token to every request.
3. **Protected routes** – Wrap routes with an `AuthGuard` component that redirects to login if token is missing/invalid.
4. **Auto‑profile check** – After login, immediately call `GET /api/v1/profile/`. If profile is `null`, open the profile creation modal automatically.

### Profile Creation/Edit Flow

- Use a multi‑step form or a modal with validation.
- Upload profile photo with preview.
- After successful creation, redirect to dashboard.

### Dashboard Design

The dashboard should display:

1. **User summary card** – Profile picture, name, goal, age, weight, height.
2. **Today’s log section** – Form to input steps, sleep, water, food (with meal‑wise input).
3. **Recent logs table** – Show last 7 days of logs with ability to edit/delete.
4. **Analytics widgets** – Summary cards, trend charts, insights, recommendations.
5. **Health score graph** – Line chart of daily scores.

### State Management Strategy

- Use TanStack Query for all server data (profile, logs, analytics). It handles caching, background updates, and optimistic updates.
- Use a lightweight store (Zustand) for client‑side UI state (e.g., modal open/close, form draft).
- Keep authentication state in a store that syncs with localStorage.

### Error Handling & Loading States

- Display loading skeletons while fetching data.
- Show toast notifications for API errors.
- Implement retry logic for failed requests.

### Responsive Design

- Mobile‑first approach; ensure all forms are usable on small screens.
- Use Tailwind’s responsive utilities for layout adjustments.

---

## Implementation Steps

### Step 1: Project Setup
```bash
npm create vite@latest preventive-healthcare-frontend -- --template react-ts
cd preventive-healthcare-frontend
npm install axios @tanstack/react-query zustand react-router-dom react-hook-form zod @hookform/resolvers recharts sonner tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### Step 2: Configure API Client
Create `src/api/client.ts` with axios instance and request/response interceptors.

### Step 3: Build Authentication Pages
- Login form with email/password.
- Signup form with email, password, timezone.
- Store token and redirect on success.

### Step 4: Create Protected Layout
- Wrap dashboard routes with `AuthGuard`.
- Implement a navigation bar with logout button.

### Step 5: Profile Modal Component
- Modal that appears automatically after login if profile is missing.
- Form with validation using Zod schema matching backend `ProfileCreate`.

### Step 6: Dashboard Page
- Fetch profile and today’s log on mount.
- Render metrics input form.
- Display recent logs in a table.

### Step 7: Analytics Integration
- Fetch summary, insights, trends, recommendations.
- Visualize with charts and cards.

### Step 8: Polish & Production Optimizations
- Add error boundaries.
- Implement code splitting.
- Set up environment variables for API base URL.
- Write unit tests for critical components.

---

## Example Code Snippets

### Axios Instance with Interceptor
```typescript
// src/api/client.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default apiClient;
```

### React Query Provider Setup
```tsx
// src/main.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById('root')!).render(
  <QueryClientProvider client={queryClient}>
    <App />
  </QueryClientProvider>
);
```

### Protected Route Component
```tsx
// src/components/auth/ProtectedRoute.tsx
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const token = localStorage.getItem('access_token');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
};
```

---

## Deployment Considerations

- Set `VITE_API_BASE_URL` environment variable to point to your production backend.
- Use HTTPS in production.
- Configure CI/CD for automated builds.
- Consider using a CDN for static assets.

---

## Conclusion

This guide provides everything needed to build a production‑ready frontend that seamlessly integrates with the Preventive Healthcare AI backend. The API is well‑structured, consistent, and fully documented. By following the recommended architecture and implementation steps, you can deliver a high‑quality user experience that meets the described workflow.

For any further questions, refer to the backend source code or contact the backend development team.