from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from app.core import VALID_TIMEZONES

# response models
class MessageResponse(BaseModel):
    message: str = Field(..., description="A status or result message from the server.")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "User logged in successfully"
            }
        }
    )
    
class TokenResponse(BaseModel):
    message: str = Field(..., description="A success message")
    access_token: str = Field(..., description="The JWT access token used for authentication")
    token_type: str = Field("bearer", description="The type of token (usually 'bearer')")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "User logged in successfully",
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    )

class UserResponse(BaseModel):
    id: int = Field(..., description="The unique identifier for the user.")
    email: str = Field(..., description="The registered email address.")
    timezone: str = Field(..., description="The user's preferred IANA timezone.")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "email": "user@example.com",
                "timezone": "Asia/Kolkata"
            }
        }
    )


# validation models
class UserCreate(BaseModel):
    email: EmailStr = Field(
        ..., 
        description="A valid email address for the user account."
    )
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=64,
        description="The user's password. Must include uppercase, lowercase, numbers, and special characters."
    )
    
    timezone: str = Field(
        "UTC",
        description="User timezone (e.g., Asia/Kolkata). Defaults to UTC."
    )

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v: str) -> str:
        v = v.strip()
        if v not in VALID_TIMEZONES:
            raise ValueError(f"Invalid timezone. Please provide a valid IANA timezone name.")
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return v.lower().strip()
    
    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Ensure password meets complexity requirements for high security."""
        
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit (0-9)")
        
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter (A-Z)")
        
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter (a-z)")
        
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(char in special_chars for char in v):
            raise ValueError(f"Password must contain at least one special character from: {special_chars}")
        
        return v 

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "SecureP@ssword123!",
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
        description="The user's account password.",
    )
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return v.lower().strip()
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "SecurePassword123!"
            }
        }
    )
    