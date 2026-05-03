from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import Optional


# response schemas
class MedicalHistoryResponse(BaseModel):
    """Schema for returning medical history record."""
    diabetes: Optional[bool] = Field(None, description="History of diabetes.")
    bp: Optional[bool] = Field(None, description="History of high blood pressure.")
    high_cholesterol: Optional[bool] = Field(None, description="History of high cholesterol.")
    heart_disease: Optional[bool] = Field(None, description="History of heart disease.")
    asthma: Optional[bool] = Field(None, description="History of asthma.")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "diabetes": True,
                "bp": False,
                "high_cholesterol": True,
                "heart_disease": False,
                "asthma": False
            }
        }
    )


# validation schemas
class MedicalHistoryCreate(BaseModel):
    """
    Schema for creating medical history.
    At least one field must be provided if the API is called.
    """
    diabetes: Optional[bool] = Field(None, description="History of diabetes.")
    bp: Optional[bool] = Field(None, description="History of high blood pressure.")
    high_cholesterol: Optional[bool] = Field(None, description="History of high cholesterol.")
    heart_disease: Optional[bool] = Field(None, description="History of heart disease.")
    asthma: Optional[bool] = Field(None, description="History of asthma.")

    @model_validator(mode="before")
    @classmethod
    def check_at_least_one(cls, data):
        """Ensures that at least one condition is provided."""
        if isinstance(data, dict) and not any(
            data.get(key) is not None for key in data
        ):
            raise ValueError("At least one medical condition must be provided")
        return data

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "diabetes": True,
                "bp": False,
                "high_cholesterol": True,
                "heart_disease": False,
                "asthma": False
            }
        }
    )
