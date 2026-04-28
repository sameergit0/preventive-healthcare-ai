from pydantic import BaseModel, ConfigDict
from typing import Dict, List

class TimezonesResponse(BaseModel):
    grouped: Dict[str, List[str]]
    
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "grouped": {
                    "Asia": ["Asia/Kolkata", "Asia/Dubai", "Asia/Tokyo"],
                    "Europe": ["Europe/London", "Europe/Paris"],
                    "Etc": ["UTC", "GMT"]
                }
            }
        }
    )