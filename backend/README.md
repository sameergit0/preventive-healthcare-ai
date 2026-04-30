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
* 📈 **Advanced Analytics Engine** – Weighted health scoring, robust trends, and personalized recommendations across all metrics
* 📂 **File Handling** – Profile image upload & static serving
* 🔄 **Database Migrations** – Alembic-based schema versioning
* ⚡ **Optimized APIs** – FastAPI async support
* 📝 **Structured Logging** – Debuggable and production-friendly logs

---

## 🛠 Tech Stack

* **Backend**: FastAPI, Python 3.12+
* **Database**: Neon PostgreSQL (serverless) + SQLAlchemy ORM
* **Migrations**: Alembic
* **Auth**: JWT + bcrypt
* **Validation**: Pydantic
* **Server**: Uvicorn
* **Config**: python-dotenv
* **Containerization**: Docker, Docker Compose

---

## 📂 Project Structure

```
app/
├── api/v1/endpoints/   # API routes
├── core/               # Security & configs
├── db/                 # DB setup
├── models/             # ORM models
├── schemas/            # Pydantic schemas
├── utils/              # Helpers (logging, timezone)
└── main.py             # Entry point

alembic/                # DB migrations
test/                   # Unit tests
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
# OR
pip install -e .
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

* Signup / Login / Current User

### 🌐 Common Timezones

* Timezone


### 👤 Profile

* Create, update, delete profile
* Upload profile image

### 📊 Health Metrics

* Daily logs (Upsert logic)
* Tracking for: Steps, Sleep (Hours/Quality), Water, Activity/Sedentary minutes, Sugar, and Fruits
* Time-series tracking

### 📈 Analytics Engine

* **Weighted Health Score**: Professional algorithm calculating overall wellness (0-100)
* **Trend Analysis**: Percentage-based comparisons between current and previous periods
* **Personalized Insights**: Auto-generated severity-based insights for all health categories
* **Actionable Recommendations**: High/Medium/Low priority health suggestions
* **Score History**: Historical health score visualization data

---

## 🧪 Testing

```bash
pytest
```

---

## 🧱 Production Considerations

* Use **Gunicorn + Uvicorn workers**
* Deploy behind **Nginx**
* Store secrets securely
* Enable HTTPS
* Use Docker for containerization

---

## 🚀 Future Improvements

* 🤖 AI-based health recommendations
* 📱 Mobile app integration
* 📊 Advanced ML analytics
* 🔔 Real-time alerts

---

## 📜 License

MIT License
