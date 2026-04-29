from app.utils import setup_logging, lifespan
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from app.api.v1 import api
from app.api.v1.endpoints import base
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

setup_logging()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")

app = FastAPI(
    title="Preventive Healthcare AI API",
    description="API for health tracking and preventive healthcare",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=base.utils_router, tags=["General"])
app.include_router(router=api.api_router, prefix="/api/v1")

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")