from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from app.core import VALID_TIMEZONES

# response models
class MessageResponse(BaseModel):
    message: str
    
class TokenResponse(BaseModel):
    message: str
    access_token: str
    token_type: str
    
class UserResponse(BaseModel):
    id: int
    email: str
    timezone: str 
    
    model_config = ConfigDict(from_attributes=True, extra="forbid")


# validation models
class UserCreate(BaseModel):
    email: EmailStr = Field(
        ..., 
        description="The email address of the user. Must be a valid email format."
    )
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=64,
        description="The user's password. Must be between 8 and 64 characters long, contain at least one uppercase letter, one lowercase letter, one number, and one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)."
    )
    
    timezone: str = Field(
        ...,
        description="User timezone (e.g., Asia/Kolkata, America/New_York)"
    )

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v: str) -> str:
        v = v.strip()
        if v not in VALID_TIMEZONES:
            raise ValueError(f"Invalid timezone. Must be a valid IANA timezone (e.g., Asia/Kolkata, America/New_York)")
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return v.lower().strip()
    
    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength requirements"""
        
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit (0-9)")
        
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter (A-Z)")
        
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter (a-z)")
        
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(char in special_chars for char in v):
            raise ValueError("Password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)")
        
        return v 

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "StrongP@ssword123",
                "timezone": "Asia/Kolkata"
            }
        }
    )
    
class UserLogin(BaseModel):
    email: EmailStr = Field(
        ..., 
        description="The registered email address of the user."
    )
    password: str = Field(
        ..., 
        min_length=1,
        description="The user's password.",
    )
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return v.lower().strip()
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "SecurePassword123"
            }
        }
    )
    