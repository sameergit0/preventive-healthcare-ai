from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import Optional, List, Literal
from datetime import date, datetime

# Response schemas
class FoodItemResponse(BaseModel):
    """Schema representing a single meal entry in the response."""
    meal: Literal["breakfast", "lunch", "dinner"] = Field(..., description="The type of meal.")
    items: List[str] = Field(..., description="List of food items consumed.")

    model_config = ConfigDict(from_attributes=True)

class DailyHealthLogResponse(BaseModel):
    """
    Comprehensive daily health report including physical metrics and food logs.
    All metrics are optional and will return None if not recorded for that day.
    """
    id: int = Field(..., description="Unique database ID for the log.")
    log_date: date = Field(..., description="The date for which this data was recorded.")
    steps: Optional[int] = Field(None, description="Step count.")
    sleep_hours: Optional[float] = Field(None, description="Hours of sleep recorded.")
    water_intake: Optional[float] = Field(None, description="Water intake in liters.")
    food_log: List[FoodItemResponse] = Field(default_factory=list, description="List of meals consumed.")
    sleep_quality: Optional[Literal["poor", "average", "good", "excellent"]] = Field(None, description="User-reported sleep quality.")
    activity_minutes: Optional[int] = Field(None, description="Minutes of physical activity.")
    sedentary_minutes: Optional[int] = Field(None, description="Minutes of sedentary time.")
    nutrition_sugar: Optional[float] = Field(None, description="Sugar intake in grams.")
    nutrition_fruits: Optional[int] = Field(None, description="Number of fruits consumed.")
    created_at: datetime = Field(..., description="Timestamp of when this log was first created.")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 101,
                "log_date": "2024-05-02",
                "steps": 8500,
                "sleep_hours": 7.5,
                "water_intake": 2.5,
                "food_log": [
                    {"meal": "breakfast", "items": ["eggs", "toast"]},
                    {"meal": "lunch", "items": ["grilled chicken", "quinoa"]}
                ],
                "sleep_quality": "good",
                "activity_minutes": 45,
                "sedentary_minutes": 300,
                "nutrition_sugar": 35.0,
                "nutrition_fruits": 2,
                "created_at": "2024-05-02T22:15:00Z"
            }
        }
    )
    
class AllLogsResponse(BaseModel):
    """Paginated response containing a collection of health logs."""
    message: str = Field(..., description="Helpful summary of the request result.")
    logs: List[DailyHealthLogResponse] = Field(..., description="List of health log records.")
    total: int = Field(..., description="Total count of logs available in the system for the current filter.")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "message": "Successfully fetched 1 log",
                "logs": [
                    {
                        "id": 101,
                        "log_date": "2024-05-02",
                        "steps": 8500,
                        "sleep_hours": 7.5,
                        "water_intake": 2.5,
                        "food_log": [],
                        "sleep_quality": "good",
                        "activity_minutes": 45,
                        "sedentary_minutes": 300,
                        "nutrition_sugar": 35.0,
                        "nutrition_fruits": 2,
                        "created_at": "2024-05-02T22:15:00Z"
                    }
                ],
                "total": 1
            }
        }
    )

# Validation schemas
class FoodItem(BaseModel):
    """Input schema for a single meal log."""
    meal: Literal["breakfast", "lunch", "dinner"] = Field(
        ...,
        description="Meal type (breakfast, lunch, or dinner)"
    )
    items: List[str] = Field(
        ...,
        min_length=1,
        description="List of food items (e.g., ['poha', 'tea'])"
    )

    model_config = ConfigDict(extra="forbid")

class DailyHealthLogCreate(BaseModel):
    """
    Input schema for daily health logging. 
    At least one metric must be provided. Unsent fields will be ignored.
    """
    steps: Optional[int] = Field(
        None, 
        ge=0, 
        le=100000, 
        description="Daily steps (0-100k)"
    )
    sleep_hours: Optional[float] = Field(
        None, 
        ge=0, 
        le=24, 
        description="Sleep duration in hours (0-24)"
    )
    water_intake: Optional[float] = Field(
        None, 
        ge=0, 
        le=10, 
        description="Water in liters (0-10)"
    )
    food_log: List[FoodItem] = Field(
        default_factory=list,
        description="Meals to add. These are appended to today's existing food log."
    )
    sleep_quality: Optional[Literal["poor","average","good","excellent"]] = Field(
        None, 
        description="Quality of sleep"
    )
    activity_minutes: Optional[int] = Field(
        None, 
        ge=0, 
        le=1440, 
        description="Active minutes (0-1440)"
    )
    sedentary_minutes: Optional[int] = Field(
        None, 
        ge=0, 
        le=1440, 
        description="Sedentary minutes (0-1440)"
    )
    nutrition_sugar: Optional[float] = Field(
        None, 
        ge=0, 
        le=500, 
        description="Sugar in grams (0-500)"
    )
    nutrition_fruits: Optional[int] = Field(
        None, 
        ge=0, 
        le=20, 
        description="Fruit count (0-20)"
    )
    
    @model_validator(mode="before")
    @classmethod
    def check_at_least_one_metric(cls, data):
        """Ensures that the user is actually logging something."""
        if isinstance(data, dict) and not any(
            key in data for key in [
                "steps", "sleep_hours", "water_intake", "food_log", 
                "sleep_quality", "activity_minutes", "sedentary_minutes", 
                "nutrition_sugar", "nutrition_fruits"
            ]
        ):
            raise ValueError("At least one health metric must be provided")
        return data
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "example": {
                "steps": 8000,
                "water_intake": 2.5,
                "food_log": [{"meal": "breakfast", "items": ["poha", "tea"]}]
            }
        }
    )
