from pydantic import BaseModel, Field, ConfigDict, field_validator, computed_field
from fastapi import Form
from typing import Literal, Optional

# response models
class ProfileResponse(BaseModel):
    id: int 
    full_name: str
    age: int
    gender: str
    weight: float
    height: float
    waist_cm: Optional[float] = None
    goal: str
    profile_image: Optional[str] = None

    @computed_field
    @property
    def bmi(self) -> Optional[float]:
        if not self.height or not self.weight or self.height <= 0 or self.weight <= 0:
            return None
        height_m = self.height / 100
        return round(self.weight / (height_m ** 2), 2)

    @computed_field
    @property
    def bmi_category(self) -> Optional[str]:
        bmi = self.bmi
        if bmi is None:
            return None
        if bmi < 18.5:
            return "Underweight"
        elif bmi < 25:
            return "Normal"
        elif bmi < 30:
            return "Overweight"
        else:
            return "Obese"

    model_config = ConfigDict(from_attributes=True, extra="forbid")
    
class ProfileGetResponse(BaseModel):
    message: str
    profile: Optional[ProfileResponse] = None
    
class ProfilePhotoResponse(BaseModel):
    message: str
    image_url: Optional[str] = None

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
        description="Primary health objective"
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
    def clean_name(cls, v: str) -> str:
        v = " ".join(v.split()) 
        if " " not in v:
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
                "weight": 72.5,
                "height": 175.0,
                "waist_cm": 80.5,
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
        description="Updated full name of the user (must include first and last name)"
    )
    age: Optional[int] = Field(
        None,
        gt=0, 
        lt=120,
        description="Updated age of the user in years"
    )
    gender: Optional[Literal["M", "F"]] = Field(
        None,
        description="Updated gender (M = Male, F = Female)"
    )
    weight: Optional[float] = Field(
        None,
        gt=20.0,
        lt=300.0,
        description="Updated weight of the user in kilograms (kg)"
    )
    height: Optional[float] = Field(
        None,
        gt=50.0,
        lt=250.0,
        description="Updated height of the user in centimeters (cm)"
    )
    waist_cm: Optional[float] = Field(
        None,
        gt=30.0,
        lt=200.0,
        description="Updated waist circumference in cm"
    )
    goal: Optional[Literal["Weight Loss", "Weight Gain", "Muscle Building", "Maintain Fitness", "Improve Sleep", "Reduce Stress"]] = Field(
        None, 
        description="Updated health or fitness goal of the user"
    )
    
    @field_validator("full_name")
    @classmethod
    def clean_name(cls, v):
        if v is None:
            return v
        v = " ".join(v.split()) 
        if " " not in v:
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
                "weight": 72.5,
                "waist_cm": 80.5,
                "goal": "Muscle Building"
            }
        }
    )