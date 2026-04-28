from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import Optional, List, Literal
from datetime import date, datetime

# response schemas
class FoodItemResponse(BaseModel):
    meal: Literal["breakfast", "lunch", "dinner"]
    items: List[str]

    model_config = ConfigDict(from_attributes=True, extra="forbid")

class DailyHealthLogResponse(BaseModel):
    id: int
    log_date: date  
    steps: Optional[int]
    sleep_hours: Optional[float]
    water_intake: Optional[float]
    food_log: List[FoodItemResponse] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, extra="forbid")
    
class AllLogsResponse(BaseModel):
    message: str
    logs: List[DailyHealthLogResponse]
    total: int

    model_config = ConfigDict(from_attributes=True, extra="forbid")

# validation schemas
class FoodItem(BaseModel):
    meal: Literal["breakfast", "lunch", "dinner"] = Field(
        ...,
        description="Type of meal consumed (breakfast, lunch, or dinner)"
    )
    items: List[str] = Field(
        ...,
        min_length=1,
        description="List of food items consumed in this meal (e.g., ['poha', 'tea'])"
    )

class DailyHealthLogCreate(BaseModel):
    steps: Optional[int] = Field(
        None,
        ge=0,
        le=100000,
        description="Total number of steps taken during the day"
    )
    sleep_hours: Optional[float] = Field(
        None,
        ge=0,
        le=24,
        description="Total hours of sleep in the last 24 hours"
    )
    water_intake: Optional[float] = Field(
        None,
        ge=0,
        le=10,
        description="Total water intake for the day in liters"
    )
    food_log: Optional[List[FoodItem]] = Field(
        [],
        description="Detailed log of meals consumed throughout the day, including meal type and food items"
    )
    
    @model_validator(mode="before")
    @classmethod
    def check_at_least_one_metric(cls, data):
        if isinstance(data, dict) and not any(key in data for key in ["steps", "sleep_hours", "water_intake", "food_log"]):
            raise ValueError("At least one health metric must be provided")
        return data
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "steps": 8000,
                "sleep_hours": 7.5,
                "water_intake": 2.5,
                "food_log": [
                    {
                        "meal": "breakfast",
                        "items": ["poha", "tea"]
                    },
                    {
                        "meal": "lunch",
                        "items": ["roti", "dal", "rice"]
                    }
                ]
            }
        }
    )