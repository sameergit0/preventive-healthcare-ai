from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import Optional, Literal

# response schemas
class LifestyleResponse(BaseModel):
    """Schema representing the user's lifestyle profile."""
    tobacco_type: Optional[str] = Field(None, description="Tobacco usage frequency.")
    passive_smoke: Optional[bool] = Field(None, description="Passive smoke exposure.")
    alcohol_freq: Optional[str] = Field(None, description="Alcohol consumption frequency.")
    alcohol_binge: Optional[bool] = Field(None, description="Binge drinking behavior.")
    stress_level: Optional[int] = Field(None, description="Stress level (1-5).")
    work_life_balance: Optional[int] = Field(None, description="Work-life balance (1-5).")
    screen_time_hours: Optional[float] = Field(None, description="Daily screen time.")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "tobacco_type": "never",
                "stress_level": 3,
                "work_life_balance": 4,
                "screen_time_hours": 5.5
            }
        }
    )

# Validation schemas
class LifestyleCreate(BaseModel):
    """
    Validation schema for creating a lifestyle profile.
    At least one field must be provided.
    """
    tobacco_type: Optional[Literal["never", "daily", "weekly", "occasionally", "former"]] = Field(
        None,
        description="Tobacco usage (never, daily, weekly, occasionally, or former)"
    )
    passive_smoke: Optional[bool] = Field(
        None,
        description="True if exposed to passive smoke"
    )
    alcohol_freq: Optional[Literal["never","rarely", "sometimes", "often", "daily"]] = Field(
        None, 
        description="Alcohol frequency (never, rarely, sometimes, often, or daily)"
    )
    alcohol_binge: Optional[bool] = Field(
        None,
        description="True if user engages in occasional heavy drinking"
    )
    stress_level: Optional[int] = Field(
        None,
        ge=1,
        le=5,
        description="Stress level from 1 (Low) to 5 (High)"
    )
    work_life_balance: Optional[int] = Field(
        None,
        ge=1,
        le=5,
        description="Work-life balance from 1 (Poor) to 5 (Excellent)"
    )
    screen_time_hours: Optional[float] = Field(
        None,
        ge=0,
        le=24,
        description="Daily screen time in hours (0-24)"
    )

    @model_validator(mode="before")
    @classmethod
    def check_at_least_one_metric(cls, data):
        """Ensures that the profile isn't completely empty if submitted."""
        if isinstance(data, dict) and not any(
            data.get(key) is not None for key in data
        ):
            raise ValueError("At least one lifestyle metric must be provided")
        return data

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "tobacco_type": "never",
                "passive_smoke": False,
                "alcohol_freq": "rarely",
                "stress_level": 2,
                "work_life_balance": 4,
                "screen_time_hours": 4.5
            }
        }
    )