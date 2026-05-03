from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Optional
from datetime import datetime

class HomeResponse(BaseModel):
    message: str = Field(..., description="Greeting message from the API")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Welcome to the Preventive Healthcare AI API."
            }
        }
    )
    
class HealthResponse(BaseModel):
    status: Literal["healthy", "degraded", "unhealthy"] = Field(
        ..., 
        description="Current health status of the API and its dependencies"
    )
    timestamp: datetime = Field(..., description="Server timestamp when the health check was performed")
    version: str = Field("1.0.0", description="API version")
    response_time_ms: Optional[float] = Field(
        None, 
        description="Database response time in milliseconds (null if unhealthy)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "timestamp": "2026-05-02T15:27:10.271845",
                "version": "1.0.0",
                "response_time_ms": 25.5
            }
        }
    )