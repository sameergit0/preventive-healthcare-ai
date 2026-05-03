import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api
from app.api.v1.endpoints import general
from app.utils import setup_logging, lifespan

# Load environment variables from .env file
load_dotenv()

# Initialize global logging configuration
setup_logging()

# Configure static uploads directory
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")

# Initialize FastAPI Application
app = FastAPI(
    title="Preventive Healthcare AI API",
    description="A comprehensive API for tracking health metrics and generating preventive healthcare insights.",
    version="1.0.0",
    lifespan=lifespan  # Handles startup/shutdown events (see app/utils/lifespan.py)
)

# --- MIDDLEWARE CONFIGURATION ---
# CORS (Cross-Origin Resource Sharing) configuration for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"  # Standard Vite/React development port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROUTER INTEGRATION ---
# General utility endpoints (Health check, etc.)
app.include_router(router=general.utils_router, tags=["General"])

# Core API v1 routes (Authentication, Metrics, Lifestyle, Analytics)
app.include_router(router=api.api_router, prefix="/api/v1")

# --- STATIC FILES ---
# Mount the uploads directory to serve profile photos and other media
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")