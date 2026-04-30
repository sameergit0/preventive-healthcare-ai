import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from .logging_config import get_logger

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events"""
    
    # ========== STARTUP ==========
    logger.info("=" * 50)
    logger.info("Starting Preventive Healthcare AI API")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"Upload directory: {os.getenv('UPLOAD_DIR', 'uploads')}")
    logger.info(f"Log level: {logging.getLevelName(logger.getEffectiveLevel())}")
    logger.info("=" * 50)
    logger.info("Application startup complete - Ready to handle requests")
    
    yield  # Application runs here
    
    # ========== SHUTDOWN ==========
    logger.info("Application shutting down...")
    logger.info("=" * 50)