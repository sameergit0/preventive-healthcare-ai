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
* 📊 **Health Metrics Tracking** – Weight, BP, glucose, lifestyle data
* 👤 **Profile Management** – User profiles with image upload
* 📈 **Analytics Engine** – Trends, summaries, and health insights
* 📂 **File Handling** – Profile image upload & static serving
* 🔄 **Database Migrations** – Alembic-based schema versioning
* ⚡ **Optimized APIs** – FastAPI async support
* 📝 **Structured Logging** – Debuggable and production-friendly logs

---

## 🛠 Tech Stack

* **Backend**: FastAPI, Python 3.12+
* **Database**: MySQL + SQLAlchemy ORM
* **Migrations**: Alembic
* **Auth**: JWT + bcrypt
* **Validation**: Pydantic
* **Server**: Uvicorn
* **Config**: python-dotenv

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
git clone <your-repo-url>
cd backend
```

---

### 2. Create virtual environment

```bash
python -m venv .venv
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
# Database
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

## 📌 API Documentation

* Swagger: http://localhost:8000/docs
* ReDoc: http://localhost:8000/redoc

---

## 🔌 Core API Modules

### 🔐 Authentication

* Signup / Login / Current User

### 👤 Profile

* Create, update, delete profile
* Upload profile image

### 📊 Health Metrics

* Daily logs (CRUD)
* Time-series tracking

### 📈 Analytics

* Health trends
* Insights
* Recommendations
* Score tracking

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
