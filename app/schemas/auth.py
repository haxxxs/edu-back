from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# Schema for user registration input
class UserRegistrationInput(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")
    name: Optional[str] = None
    telegram_id: str = Field(..., description="Telegram ID or username (must start with @ or be numeric)")

# Schema for user login input
class UserLoginInput(BaseModel):
    email: EmailStr # Can use alias if frontend sends 'username'
    password: str

# Schema for the response after successful login
class AuthResponse(BaseModel):
    access_token: str = Field(..., alias="token")
    token_type: str = "bearer" # Typically included
    is_admin: bool = False
    user_id: int
    email: EmailStr
    telegram_id: Optional[str] = None
    
    class Config:
        allow_population_by_field_name = True

# Schema for a simple message response
class MessageResponse(BaseModel):
    message: str 