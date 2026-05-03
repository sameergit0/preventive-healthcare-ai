# 🚀 Preventive Healthcare AI Backend

A **scalable FastAPI backend system** for preventive healthcare, enabling users to track health metrics, analyze trends, and receive personalized insights.

---

## 🧠 Overview

This project is designed to support **preventive healthcare systems** by combining:

* 📊 Health data tracking
* 📈 Analytics & insights
* 🔐 Secure authentication
* ⚡ High-performance API architecture

It follows a **modular, production-ready backend design** suitable for real-world healthcare applications.

---

## ✨ Key Features

* 🔐 **JWT Authentication** – Secure login & user management
* 📊 **Expanded Health Metrics** – Tracking for Steps, Sleep (Hours & Quality), Water, Activity, Sedentary time, and Nutrition (Sugar/Fruits)
* 👤 **Profile Management** – BMI calculation, waist circumference tracking, and photo management
* 🏥 **Medical History** – tracking for chronic conditions (Diabetes, Hypertension, Heart Disease, Asthma) and cholesterol
* 🤖 **Digital Health Coach** – Prioritized task system that analyzes performance gaps to provide actionable improvements
* 📈 **Advanced Analytics Engine** – Weighted health scoring, robust trends, and personalized insights
* 📂 **File Handling** – Profile image upload & static serving
* 🔄 **Database Migrations** – Alembic-based schema versioning
* ⚡ **Optimized APIs** – FastAPI async support with structured response models
* 📝 **Structured Logging** – Professional logging across all core modules for production observability

---

## 🛠 Tech Stack

* **Backend**: FastAPI (Python 3.12+)
* **Database**: Neon PostgreSQL (Serverless) + SQLAlchemy ORM
* **Migrations**: Alembic
* **Auth**: JWT + Passlib (bcrypt)
* **Validation**: Pydantic v2
* **Server**: Uvicorn
* **Environment**: python-dotenv
* **Dependency Management**: uv
* **Containerization**: Docker & Docker Compose

---

## 📂 Project Structure

```
app/
├── api/v1/endpoints/   # Auth, Metrics, Lifestyle, Profile, Medical, Analytics
├── core/               # Security, App Configs, Health Constants
├── db/                 # DB Session, Base Model, Dependency Injection
├── models/             # SQLAlchemy ORM Models (User, Health, Profile, etc.)
├── schemas/            # Pydantic Models for Request/Response Validation
├── utils/              # Analytics Helpers, Logging, Lifespan, Timezone
└── main.py             # Entry point (FastAPI App & Middleware)

alembic/                # Database Migrations (Versions & Env)
logs/                   # Application log files
test/                   # Unit and Integration tests
uploads/                # User-uploaded profile photos
```

---

## ⚙️ Setup Instructions

### 1. Clone repo

```bash
git clone https://github.com/sameergit0/preventive-healthcare-ai.git
cd backend
```

---

### 2. Create virtual environment

```bash
uv venv
.venv\Scripts\activate
```

---

### 3. Install dependencies

```bash
uv sync
```

---

### 4. Configure Environment

```bash
cp .env.example .env
```

Example:

```env
# ===============================
# Database (Neon PostgreSQL)
# ===============================
DATABASE_URL="dialect+driver://username:password@host:port/database"

# ===============================
# File Storage
# ===============================
UPLOAD_DIR=uploads
LOG_DIR=logs

# ===============================
# Password Hashing
# ===============================
H_ALGORITHM=bcrypt

# ===============================
# Authentication (JWT)
# ===============================
AK_SECRET_KEY="your-secret-key"
AK_ALGORITHM=HS256
AK_ACCESS_TOKEN_EXPIRE_MINUTES=60

# ===============================
# Base URL
# ===============================
BASE_URL=http://localhost:8000
```

---

### 5. Run migrations

```bash
alembic upgrade head
```

---

### 6. Start server

```bash
uvicorn app.main:app --reload
```

---

## 🐳 Docker Deployment

### Build and run with Docker

```bash
# Build the Docker image
docker build -t preventive-health-backend .

# Run the container
docker run -p 8000:8000 --env-file .env preventive-health-backend
```

### Using Docker Compose

```bash
# Start services with build
docker compose up --build -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

> **Note**: Ensure your `.env` file is properly configured before running Docker containers.

---

## 📌 API Documentation

* Swagger: http://localhost:8000/docs
* ReDoc: http://localhost:8000/redoc

---

## 🔌 Core API Modules

### 🔐 Authentication
* Signup / Login / Current User session management.

### 🏥 Medical History
* Track chronic conditions (Diabetes, BP, Heart Disease, etc.) to influence health scoring.

### 👤 Profile & Lifestyle
* **Profile**: Management of BMI, physical goals, and profile photo management.
* **Lifestyle**: Tracking of Stress, Work-Life Balance, and habits (Alcohol/Tobacco).

### 📊 Health Metrics
* Daily logs for: Steps, Sleep, Water, Activity, Sedentary, Sugar, and Fruits.
* Context-aware **Upsert** logic (Update or Insert depending on date).

### 📈 Analytics Engine & Digital Coach
The Analytics engine provides a holistic view of user wellness by correlating behavior with medical and physical context.

* **`/analytics/status`**: **Dashboard Hero API**. Returns an all-time overall health score and risk category.
* **`/analytics/summary`**: **Health Summary API**. Aggregates core health metrics (Steps, Sleep, Water, etc.) over a filtered period.
* **`/analytics/insights`**: **Behavioral Analysis**. Generates personalized insights based on recent trends.
* **`/analytics/trends`**: **Progress Visualization**. Provides day-by-day health scores.
* **`/analytics/recommendations`**: **Digital Coach**. Prioritizes tasks to address the most critical health gaps.

### 🛠 System Utilities
* **`/health`**: Comprehensive health check (Database connectivity & response time).
* **`/`**: Root welcome endpoint.

---

## 🧪 Testing

```bash
pytest
```

---

## 🧱 Production Considerations

* Use **Gunicorn + Uvicorn workers**
* Deploy behind **Nginx**
* Store secrets securely and enable HTTPS
* Use Docker for containerization

---

## 🚀 Future Improvements

* 🤖 AI-powered health recommendations
* 📱 Mobile app integration
* 📊 Advanced ML predictive analytics
* 🔔 Real-time alerts & notifications

---

## 📜 License

MIT License
