import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from .logging_config import get_logger

# Initialize logger for lifecycle events
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    Handles resource initialization and cleanup (e.g., directory creation, connection pooling).
    """
    
    # ========== [1] STARTUP SEQUENCE ==========
    logger.info("=" * 60)
    logger.info("[STARTUP] INITIALIZING PREVENTIVE HEALTHCARE AI BACKEND")
    
    # Diagnostic Information
    upload_dir = os.getenv("UPLOAD_DIR", "uploads")
    log_level = logging.getLevelName(logger.getEffectiveLevel())
    
    logger.info(f"Upload Dir: {upload_dir}")
    logger.info(f"Log Level: {log_level}")
    
    # Resource Initialization: Ensure upload directories exist
    if not os.path.exists(upload_dir):
        logger.info(f"Creating missing upload directory: {upload_dir}")
        os.makedirs(upload_dir, exist_ok=True)
        
    logger.info("=" * 60)
    logger.info("STARTUP COMPLETE - Accepting connections")
    
    # --- APPLICATION IS RUNNING ---
    yield  
    
    # ========== [2] SHUTDOWN SEQUENCE ==========
    logger.info("=" * 60)
    logger.info("[SHUTDOWN] SHUTTING DOWN - Releasing resources")
    
    # Add cleanup logic here if needed (e.g., closing background tasks)
    
    logger.info("Shutdown complete")
    logger.info("=" * 60)