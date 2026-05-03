from pydantic import BaseModel, Field, ConfigDict, field_validator, computed_field
from fastapi import Form, Request
from typing import Literal, Optional

# response models
class ProfileResponse(BaseModel):
    id: int = Field(..., description="The unique database ID for the profile.")
    full_name: str = Field(..., description="The user's title-cased full name.")
    age: int = Field(..., description="The user's current age.")
    gender: str = Field(..., description="Biological sex (M/F).")
    weight: float = Field(..., description="Weight in kg.")
    height: float = Field(..., description="Height in cm.")
    waist_cm: Optional[float] = Field(None, description="Waist circumference in cm.")
    goal: str = Field(..., description="The primary health or fitness objective.")
    profile_image: Optional[str] = Field(None, description="The URL to the user's profile picture.")

    @computed_field
    @property
    def bmi(self) -> float:
        """Calculates Body Mass Index (BMI) based on the user's current height and weight."""
        if self.height <=0 or self.weight <= 0:
            return 0.0
        height_m = self.height / 100
        return round(self.weight / (height_m ** 2), 2)

    @computed_field
    @property
    def bmi_category(self) -> str:
        """Determines the standard WHO weight category based on the calculated BMI."""
        if self.height <=0 or self.weight <= 0:
            return "N/A"
        if self.bmi < 18.5:
            return "Underweight"
        elif self.bmi < 25:
            return "Normal"
        elif self.bmi < 30:
            return "Overweight"
        else:
            return "Obese"

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "full_name": "John Doe",
                "age": 28,
                "gender": "M",
                "weight": 75.5,
                "height": 180.0,
                "waist_cm": 85.0,
                "goal": "Muscle Building",
                "profile_image": "https://api.example.com/uploads/profile_1.jpg",
                "bmi": 23.3,
                "bmi_category": "Normal"
            }
        }
    )
    
# validation models
class ProfileCreate(BaseModel):
    full_name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        pattern=r"^[a-zA-Z\s.'-]+$",
        description="Full name of the user (first and last name)"
    )
    age: int = Field(
        ...,
        gt=0, 
        lt=120,
        description="Age of the user in years"
    )
    gender: Literal["M", "F"] = Field(
        ...,
        description="Biological sex for physiological calculations (M = Male, F = Female)"
    )
    weight: float = Field(
        ...,
        gt=20.0,
        lt=300.0,
        description="Weight of the user in kilograms (kg)"
    )
    height: float = Field(
        ...,
        gt=50.0,
        lt=250.0,
        description="Height of the user in centimeters (cm)"
    )
    waist_cm: Optional[float] = Field(
        None,
        gt=30.0,
        lt=200.0,
        description="Waist circumference in cm"
    )
    goal: Literal["Weight Loss", "Weight Gain", "Muscle Building", "Maintain Fitness", "Improve Sleep", "Reduce Stress"] = Field(
        ..., 
        description="Primary health or fitness objective."
    )
    
    @classmethod
    def as_form(
        cls,
        full_name: str = Form(...),
        age: int = Form(...),
        gender: Literal["M", "F"] = Form(...),
        weight: float = Form(...),
        height: float = Form(...),
        waist_cm: Optional[float] = Form(None),
        goal: Literal["Weight Loss", "Weight Gain", "Muscle Building", "Maintain Fitness", "Improve Sleep", "Reduce Stress"] = Form(...)
    ):
        return cls(
            full_name=full_name,
            age=age,
            gender=gender,
            weight=weight,
            height=height,
            waist_cm=waist_cm,
            goal=goal
        )

    @field_validator("full_name")
    @classmethod
    def clean_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = " ".join(v.split()) 
        if len(v.split()) < 2:
            raise ValueError("Please provide both first and last name")
        return v.title()


    @field_validator("weight", "height", "waist_cm")
    @classmethod
    def round_values(cls, value: Optional[float]) -> Optional[float]:
        if value is None:
            return value
        return round(value, 2)
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "example": {
                "full_name": "John Doe",
                "age": 28,
                "gender": "M",
                "weight": 75.5,
                "height": 180.0,
                "waist_cm": 85.0,
                "goal": "Muscle Building"
            }
        }
    )
    

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(
        None,
        min_length=3,
        max_length=100,
        pattern=r"^[a-zA-Z\s.'-]+$",
        description="Update full name (title-cased automatically)."
    )
    age: Optional[int] = Field(
        None,
        gt=0, 
        lt=120,
        description="Update age (1-119)."
    )
    gender: Optional[Literal["M", "F"]] = Field(
        None,
        description="Update biological sex (M/F)."
    )
    weight: Optional[float] = Field(
        None,
        gt=20.0,
        lt=300.0,
        description="Update weight in kilograms (kg)."
    )
    height: Optional[float] = Field(
        None,
        gt=50.0,
        lt=250.0,
        description="Update height in centimeters (cm)."
    )
    waist_cm: Optional[float] = Field(
        None,
        gt=30.0,
        lt=200.0,
        description="Update waist circumference in cm."
    )
    goal: Optional[Literal["Weight Loss", "Weight Gain", "Muscle Building", "Maintain Fitness", "Improve Sleep", "Reduce Stress"]] = Field(
        None, 
        description="Update primary health or fitness goal."
    )

    @classmethod
    def as_form(
        cls,
        full_name: Optional[str] = Form(None),
        age: Optional[int] = Form(None),
        gender: Optional[Literal["M", "F"]] = Form(None),
        weight: Optional[float] = Form(None),
        height: Optional[float] = Form(None),
        waist_cm: Optional[float] = Form(None),
        goal: Optional[Literal["Weight Loss", "Weight Gain", "Muscle Building", "Maintain Fitness", "Improve Sleep", "Reduce Stress"]] = Form(None)
    ):
        return cls(
            full_name=full_name,
            age=age,
            gender=gender,
            weight=weight,
            height=height,
            waist_cm=waist_cm,
            goal=goal
        )

    @field_validator("full_name")
    @classmethod
    def clean_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = " ".join(v.split()) 
        if len(v.split()) < 2:
            raise ValueError("Please provide both first and last name")
        return v.title()
    
    @field_validator("weight", "height", "waist_cm")
    @classmethod
    def round_values(cls, value: Optional[float]) -> Optional[float]:
        if value is None:
            return value
        return round(value, 2)
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "example": {
                "weight": 75.5,
                "goal": "Muscle Building"
            }
        }
    )