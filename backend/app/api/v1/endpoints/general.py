from fastapi import APIRouter, status
from app.schemas import HomeResponse, HealthResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import Depends
from app.api.deps import get_db
from datetime import datetime
import time
from app.utils import get_logger

utils_router = APIRouter()
logger = get_logger(__name__)


@utils_router.get(
    "/", 
    status_code=status.HTTP_200_OK, 
    response_model=HomeResponse,  
    summary="API Root / Welcome",
    description="Returns a welcome message to verify the API is running and accessible."
)
def home() -> HomeResponse:  
    """
    Welcome endpoint for the Preventive Healthcare AI API.
    
    Returns:
        HomeResponse: A simple message object.
    """
    logger.debug("Home endpoint accessed")
    
    return HomeResponse(  
        message="Welcome to the Preventive Healthcare AI API."
    )
    
@utils_router.get(
    "/health", 
    status_code=status.HTTP_200_OK, 
    response_model=HealthResponse, 
    summary="System Health Status",
    description="Performs a health check on the API and its core dependencies (Database)."
)
def health_check(
    db: Session = Depends(get_db)
) -> HealthResponse:
    """
    Comprehensive health check endpoint.
    
    Checks:
    - Database connectivity
    - Database response time
    - API Versioning
    """
    logger.debug("Health check endpoint accessed")
    
    response_time = None
    
    try:
        start = time.time()
        # Test database connectivity
        db.execute(text("SELECT 1"))
        response_time = (time.time() - start) * 1000  
        
        if response_time <= 500:
            status = "healthy"      
            logger.debug(f"Health check: {status} - Response time: {response_time:.2f}ms")
        else:
            status = "degraded"   
            logger.warning(f"Health check: {status} - Response time: {response_time:.2f}ms (>500ms threshold)") 
            
    except Exception as e:
        status = "unhealthy"
        response_time = None
        
        logger.error(f"Health check: {status} - Database error: {str(e)}", exc_info=True)
    
    return HealthResponse(
        status=status,
        timestamp=datetime.now(),
        version="1.0.0",
        response_time_ms=response_time
    )