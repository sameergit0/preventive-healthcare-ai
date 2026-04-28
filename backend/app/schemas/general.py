from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime

class HomeResponse(BaseModel):
    message: str
    
class HealthResponse(BaseModel):
    status: Literal["healthy", "degraded", "unhealthy"]
    timestamp: datetime
    version: str = "1.0.0"
    response_time_ms: Optional[float] = None  