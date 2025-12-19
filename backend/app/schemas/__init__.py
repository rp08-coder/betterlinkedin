"""
Pydantic schemas for request/response validation
"""

from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    UserProfileUpdate,
    Token,
    NotificationPreferences
)
from app.schemas.job import (
    JobResponse,
    JobQueueResponse,
    SwipeAction
)
from app.schemas.application import (
    ApplicationResponse,
    ApplicationStatusUpdate,
    CustomResponse
)

__all__ = [
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "UserProfileUpdate",
    "Token",
    "NotificationPreferences",
    "JobResponse",
    "JobQueueResponse",
    "SwipeAction",
    "ApplicationResponse",
    "ApplicationStatusUpdate",
    "CustomResponse",
]
