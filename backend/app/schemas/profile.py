from pydantic import BaseModel, Field, ConfigDict, field_validator
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
    goal: str
    profile_image: Optional[str] = None

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
        gt=30.0,
        lt=300.0,
        description="Weight of the user in kilograms (kg)"
    )
    height: float = Field(
        ...,
        gt=50.0,
        lt=250.0,
        description="Height of the user in centimeters (cm)"
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
        goal: Literal["Weight Loss", "Weight Gain", "Muscle Building", "Maintain Fitness", "Improve Sleep", "Reduce Stress"] = Form(...)
    ):
        return cls(
            full_name=full_name,
            age=age,
            gender=gender,
            weight=weight,
            height=height,
            goal=goal
        )
    
    @field_validator("full_name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        v = " ".join(v.split()) 
        if " " not in v:
            raise ValueError("Please provide both first and last name")
        return v.title()
    
    @field_validator("weight", "height")
    @classmethod
    def round_values(cls, value: float) -> float:
        return round(value, 2)
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "full_name": "John Doe",
                "age": 28,
                "gender": "M",
                "weight": 72.5,
                "height": 175.0,
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
        gt=30.0,
        lt=300.0,
        description="Updated weight of the user in kilograms (kg)"
    )
    height: Optional[float] = Field(
        None,
        gt=50.0,
        lt=250.0,
        description="Updated height of the user in centimeters (cm)"
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
    
    @field_validator("weight", "height")
    @classmethod
    def round_values(cls, value):
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
                "goal": "Muscle Building"
            }
        }
    )