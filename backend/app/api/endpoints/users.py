"""
User endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse, UserProfileUpdate, UserProfile, NotificationPreferences

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user profile

    Args:
        current_user: Authenticated user

    Returns:
        User profile data
    """
    # Build profile from user data
    profile = UserProfile(
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        city=current_user.city or "",
        resume_url=current_user.resume_url,
        sectors=current_user.sectors or [],
        job_types=current_user.job_types or [],
        skills=current_user.skills or [],
        years_experience=current_user.years_experience,
        salary_min=current_user.salary_min,
        phone=current_user.phone,
        daily_application_limit=current_user.daily_application_limit,
        notification_preferences=NotificationPreferences(
            **current_user.notification_preferences
        ) if current_user.notification_preferences else NotificationPreferences()
    )

    return UserResponse(
        user_id=current_user.user_id,
        email=current_user.email,
        profile=profile
    )


@router.put("/profile", response_model=UserProfile)
async def update_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user profile

    Args:
        profile_update: Profile update data
        current_user: Authenticated user
        db: Database session

    Returns:
        Updated profile data
    """
    # Update fields if provided
    update_data = profile_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if field == "notification_preferences" and value is not None:
            # Convert Pydantic model to dict
            current_user.notification_preferences = value.model_dump()
        else:
            setattr(current_user, field, value)

    await db.flush()
    await db.refresh(current_user)

    # Return updated profile
    profile = UserProfile(
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        city=current_user.city or "",
        resume_url=current_user.resume_url,
        sectors=current_user.sectors or [],
        job_types=current_user.job_types or [],
        skills=current_user.skills or [],
        years_experience=current_user.years_experience,
        salary_min=current_user.salary_min,
        phone=current_user.phone,
        daily_application_limit=current_user.daily_application_limit,
        notification_preferences=NotificationPreferences(
            **current_user.notification_preferences
        ) if current_user.notification_preferences else NotificationPreferences()
    )

    return profile
