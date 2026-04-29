# 🚀 Preventive Healthcare AI System

A **full-stack AI-powered preventive healthcare platform** designed to track health metrics, analyze trends, and provide intelligent insights for better lifestyle decisions.

---

## 🧠 Overview

This project aims to build a **scalable healthcare system** that helps users:

* 📊 Track daily health metrics (weight, BP, glucose, etc.)
* 📈 Analyze trends over time
* 🤖 Get AI-driven health insights (upcoming)
* 🔐 Securely manage profiles and data

---

## 🏗️ Project Structure

```
preventive-healthcare-ai/
│
├── backend/        # FastAPI backend (APIs, DB, auth)
├── frontend/       # React frontend (Vite + TypeScript)
│
├── .gitignore      # Combined ignores for backend & frontend
└── README.md
```

---

## ⚙️ Tech Stack

### Backend

* FastAPI
* SQLAlchemy
* MySQL / PostgreSQL
* Alembic
* JWT Authentication

### Frontend

* React 19 with TypeScript
* Vite – fast build tool & dev server
* Tailwind CSS – utility-first styling
* React Router DOM – client-side routing
* TanStack Query (React Query) – data fetching & caching
* Zod – schema validation
* React Hook Form – form handling
* Zustand – state management
* Recharts – data visualization
* Axios – HTTP client

### Future Enhancements

* Machine Learning models
* AI-based recommendations
* Real-time analytics

---

## 🚀 Getting Started

### Backend Setup

```bash
cd backend
docker compose up --build -d  # starts backend server at http://localhost:8000
```

Follow instructions in: 👉 `backend/README.md`

### Frontend Setup

```bash
cd frontend
npm install  
npm run dev   # starts frontend server at http://localhost:5173
```

Detailed frontend documentation: 👉 `frontend/README.md`

---

## 🔑 Features

* 🔐 Authentication (JWT-based)
* 👤 User Profile Management
* 📊 Health Metrics Logging
* 📈 Analytics & Trends
* 📂 File Uploads (profile images)
* 📝 Logging system

---

## 🎯 Vision

To build a **preventive healthcare ecosystem** that leverages **AI + data analytics** to help users make smarter health decisions.

---

## 🚀 Future Scope

* 🤖 AI health recommendations
* 📱 Mobile app integration
* 📊 Advanced dashboards
* 🔔 Smart alerts & notifications

---

## 📜 License

MIT License
