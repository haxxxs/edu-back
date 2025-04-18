from pydantic import BaseModel, EmailStr, Field

# Schema for user registration input
class UserRegistrationInput(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")

# Schema for user login input
class UserLoginInput(BaseModel):
    email: EmailStr # Can use alias if frontend sends 'username'
    password: str

# Schema for the response after successful login
class AuthResponse(BaseModel):
    token: str
    token_type: str = "bearer" # Typically included

# Schema for a simple message response
class MessageResponse(BaseModel):
    message: str 