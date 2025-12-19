"""
User schemas for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class NotificationPreferences(BaseModel):
    """Notification preferences schema"""
    enable_new_jobs: bool = True
    enable_application_updates: bool = True
    enable_weekly_summary: bool = True
    quiet_hours_start: int = Field(22, ge=0, le=23)
    quiet_hours_end: int = Field(8, ge=0, le=23)


class UserCreate(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserProfileUpdate(BaseModel):
    """Schema for updating user profile"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    sectors: Optional[List[str]] = None
    job_types: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    years_experience: Optional[int] = Field(None, ge=0)
    salary_min: Optional[int] = Field(None, ge=0)
    daily_application_limit: Optional[int] = Field(None, ge=1, le=50)
    notification_preferences: Optional[NotificationPreferences] = None


class UserProfile(BaseModel):
    """User profile schema"""
    first_name: str
    last_name: str
    city: str
    resume_url: Optional[str] = None
    sectors: List[str] = []
    job_types: List[str] = []
    skills: List[str] = []
    years_experience: int = 0
    salary_min: Optional[int] = None
    phone: Optional[str] = None
    daily_application_limit: int = 10
    notification_preferences: NotificationPreferences

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """User response schema"""
    user_id: UUID
    email: str
    profile: Optional[UserProfile] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """Token payload data"""
    sub: UUID
    exp: datetime
    type: str
