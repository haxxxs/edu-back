from pydantic import BaseModel, Field, ConfigDict, EmailStr, HttpUrl
from datetime import datetime
from typing import Optional
from app.models.user import UserRole

# Optional stats schema (can be added later)
# class UserStats(BaseModel):
#     completedCourses: int = 0
#     activeCourses: int = 0
#     attendedEvents: int = 0

# Base properties shared by user schemas
class UserBase(BaseModel):
    email: EmailStr = Field(..., description="User's unique email address")
    name: Optional[str] = Field(None, max_length=100, description="User's display name")
    role: UserRole = Field(UserRole.STUDENT, description="User's role on the platform")
    avatar_url: Optional[HttpUrl] = Field(None, alias="avatarUrl", description="URL of the user's avatar image")
    about: Optional[str] = Field(None, description="User's self-description")
    location: Optional[str] = Field(None, max_length=100, description="User's location")
    is_active: Optional[bool] = True

    class Config:
        orm_mode = True
        allow_population_by_field_name = True # Allow avatarUrl
        use_enum_values = True # Serialize enum to its value

# Schema for creating a user in the database (internal)
class UserCreate(UserBase):
    password: str # Plain password during creation

# Schema for reading user data from DB (includes hashed password)
class UserInDB(UserBase):
    id: int
    hashed_password: str
    created_at: datetime

# Schema for the user profile API response (GET /api/auth/profile)
class UserProfile(BaseModel):
    id: int
    name: Optional[str] = None
    email: EmailStr
    role: UserRole
    avatarUrl: Optional[HttpUrl] = Field(None, description="URL of the user's avatar image") # Note the alias name
    about: Optional[str] = None
    location: Optional[str] = None
    joinedAt: datetime = Field(..., description="Timestamp when the user registered") # Note the alias name
    # stats: Optional[UserStats] = None # Add later if needed

    class Config:
        orm_mode = True # Needed to map from User ORM model
        use_enum_values = True # Serialize enum to its value
