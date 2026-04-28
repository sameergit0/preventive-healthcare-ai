from fastapi import APIRouter, status
from app.schemas import HomeResponse, HealthResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import Depends
from app.api.deps import get_db
from datetime import datetime
import time
import logging

utils_router = APIRouter()
logger = logging.getLogger(__name__)


@utils_router.get(
    "/", 
    status_code=status.HTTP_200_OK, 
    response_model=HomeResponse,  
    summary="Home Endpoint"
)
def home() -> HomeResponse:  
    """Welcome endpoint for the Preventive Healthcare AI API"""
    
    logger.debug("Home endpoint accessed")
    
    return HomeResponse(  
        message="Welcome to the Preventive Healthcare AI API."
    )

    
@utils_router.get(
    "/health", 
    status_code=status.HTTP_200_OK, 
    response_model=HealthResponse, 
    summary="Health check endpoint"
)
def health_check(db: Session = Depends(get_db)) -> HealthResponse:
    """Comprehensive health check endpoint"""
    
    response_time = None
    
    try:
        start = time.time()
        db.execute(text("SELECT 1"))
        db.commit()
        response_time = (time.time() - start) * 1000  
        
        if response_time <= 500:
            status = "healthy"      
            logger.debug(f"Health check: {status} - Response time: {response_time:.2f}ms")
        else:
            status = "degraded"   
            logger.warning(f"Health check: {status} - Response time: {response_time:.2f}ms (>500ms threshold)") 
            
    except Exception as e:
        print(f"Health check failed: {e}")  
        status = "unhealthy"
        response_time = None
        
        logger.error(f"Health check: {status} - Database error: {str(e)}", exc_info=True)
    
    return HealthResponse(
        status=status,
        timestamp=datetime.now(),
        version="1.0.0",
        response_time_ms=response_time
    )