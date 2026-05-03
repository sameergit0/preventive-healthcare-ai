from pydantic import BaseModel, ConfigDict, Field
from typing import Dict, List

class TimezonesResponse(BaseModel):
    grouped: Dict[str, List[str]] = Field(
        ..., 
        description="A dictionary mapping regions (e.g., 'Asia') to lists of full timezone strings (e.g., 'Asia/Kolkata')"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "grouped": {
                    "Asia": ["Asia/Kolkata", "Asia/Dubai", "Asia/Tokyo"],
                    "Europe": ["Europe/London", "Europe/Paris"],
                    "Other": ["UTC", "GMT"]
                }
            }
        }
    )