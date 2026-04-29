# 🏥 Preventive Healthcare AI – Frontend

A modern React-based frontend for the Preventive Healthcare AI platform. Provides an intuitive interface for users to track health metrics, view analytics, and manage their profiles.

---

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm/yarn/pnpm
- Backend server running (see [backend README](../backend/README.md))

---

### 1. Installation

```bash
cd frontend
npm install   
```

---

### 2. Configure Environment

```bash
cp .env.example .env
```

---

Example:

```env
# ===============================
# Base URL
# ===============================
VITE_API_BASE_URL=http://localhost:8000
```

---

### 3. Development

Start the development server:

```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

### 4. Build for Production

```bash
npm run build
```

Preview the production build:

```bash
npm run preview
```

---

## 🛠️ Tech Stack

- **React 19** with TypeScript
- **Vite** – fast build tool & dev server
- **Tailwind CSS** – utility-first styling
- **React Router DOM** – client-side routing
- **TanStack Query (React Query)** – data fetching & caching
- **Zod** – schema validation
- **React Hook Form** – form handling
- **Zustand** – state management
- **Recharts** – data visualization
- **Lucide React** – icon library
- **Sonner** – toast notifications
- **Axios** – HTTP client

---

## 📁 Project Structure

```
frontend/
├── public/              # Static assets
├── src/
│   ├── app/            # App-level config (router, providers, guards)
│   ├── assets/         # Images, SVGs
│   ├── components/     # Reusable UI components
│   │   ├── layout/     # Layout components
│   │   └── ui/         # Base UI primitives
│   ├── features/       # Feature‑based modules
│   │   ├── auth/       # Authentication pages & logic
│   │   ├── dashboard/  # Dashboard page
│   │   ├── profile/    # Profile management
│   │   └── analytics/  # Analytics & charts
│   ├── lib/            # Utilities, API client, validation
│   ├── stores/         # Zustand stores
│   └── types/          # TypeScript definitions
├── index.html
├── vite.config.ts
├── tailwind.config.js
└── package.json
```

---

## 🔌 API Integration

The frontend communicates with the FastAPI backend. The base URL is configured in `src/lib/api.ts`. By default it points to `http://localhost:8000/api/v1`.

---

### Environment Variables

Create a `.env` or `cp .env.example .env` file in the frontend root to override: 

```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## 🧪 Available Scripts

- `npm run dev` – start dev server with HMR
- `npm run build` – build for production
- `npm run lint` – run ESLint
- `npm run preview` – locally preview production build

---

## 🧩 Key Features

- **JWT‑based authentication** – login, signup, protected routes
- **Health metric tracking** – log weight, blood pressure, glucose, etc.
- **Interactive dashboards** – charts & trends using Recharts
- **Profile management** – upload photo, edit personal details
- **Responsive design** – works on mobile & desktop
- **Real‑time data** – TanStack Query for automatic refetching

---

## 📚 Learn More

- [React Documentation](https://react.dev)
- [Vite Documentation](https://vitejs.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [TanStack Query](https://tanstack.com/query/latest)

---

## 🚧 Future Enhancements

- Offline support with service workers
- Push notifications for health reminders
- Dark/light theme toggle
- PWA installation
- Integration with wearable APIs

---