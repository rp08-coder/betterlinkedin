"""
Application endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.application import Application, ApplicationStatus
from app.schemas.application import (
    ApplicationResponse,
    ApplicationStatusUpdate,
    CustomResponsesSubmit,
    ApplicationNoteUpdate,
    CustomResponse,
    OfferDetails
)
from app.schemas.job import JobResponse

router = APIRouter()


@router.get("/", response_model=List[ApplicationResponse])
async def get_applications(
    status_filter: Optional[ApplicationStatus] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all applications for current user

    Args:
        status_filter: Optional filter by application status
        current_user: Authenticated user
        db: Database session

    Returns:
        List of applications
    """
    query = select(Application).where(Application.user_id == current_user.user_id)

    if status_filter:
        query = query.where(Application.status == status_filter)

    result = await db.execute(query.order_by(Application.date_swiped.desc()))
    applications = result.scalars().all()

    # Convert to response format
    response = []
    for app in applications:
        job_response = JobResponse(
            job_id=app.job.job_id,
            source_url=app.job.source_url,
            company_name=app.job.company_name,
            company_logo_url=app.job.company_logo_url,
            job_title=app.job.job_title,
            description=app.job.description,
            requirements=app.job.requirements,
            job_category=app.job.job_category,
            sector=app.job.sector,
            location=app.job.location,
            date_posted=app.job.date_posted,
            is_active=app.job.is_active,
            application_url=app.job.application_url,
            application_platform=app.job.application_platform,
            custom_questions=app.job.custom_questions
        )

        # Parse custom responses if exists
        custom_responses = None
        if app.custom_responses:
            custom_responses = [
                CustomResponse(**resp) for resp in app.custom_responses
            ]

        # Parse offer details if exists
        offer_details = None
        if app.offer_details:
            offer_details = OfferDetails(**app.offer_details)

        response.append(ApplicationResponse(
            application_id=app.application_id,
            user_id=app.user_id,
            job=job_response,
            status=app.status,
            date_swiped=app.date_swiped,
            date_applied=app.date_applied,
            custom_responses=custom_responses,
            cover_letter=app.cover_letter,
            notes=app.notes,
            interview_stage=app.interview_stage,
            offer_details=offer_details
        ))

    return response


@router.put("/{application_id}/status", status_code=status.HTTP_200_OK)
async def update_application_status(
    application_id: str,
    status_update: ApplicationStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update application status

    Args:
        application_id: Application ID
        status_update: New status
        current_user: Authenticated user
        db: Database session

    Returns:
        Success message
    """
    # Get application
    result = await db.execute(
        select(Application)
        .where(
            and_(
                Application.application_id == application_id,
                Application.user_id == current_user.user_id
            )
        )
    )
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    # Update status
    application.status = status_update.status
    await db.flush()

    return {"status": "success", "message": "Application status updated"}


@router.post("/{application_id}/responses", status_code=status.HTTP_200_OK)
async def submit_custom_responses(
    application_id: str,
    responses: CustomResponsesSubmit,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit custom question responses for an application

    Args:
        application_id: Application ID
        responses: Custom question responses
        current_user: Authenticated user
        db: Database session

    Returns:
        Success message
    """
    # Get application
    result = await db.execute(
        select(Application)
        .where(
            and_(
                Application.application_id == application_id,
                Application.user_id == current_user.user_id
            )
        )
    )
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    # Update responses and mark as applied
    application.custom_responses = [resp.model_dump() for resp in responses.responses]
    application.status = ApplicationStatus.APPLIED
    application.date_applied = datetime.utcnow()

    await db.flush()

    return {"status": "success", "message": "Responses submitted"}


@router.put("/{application_id}/notes", status_code=status.HTTP_200_OK)
async def update_application_notes(
    application_id: str,
    note_update: ApplicationNoteUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update application notes

    Args:
        application_id: Application ID
        note_update: Notes update
        current_user: Authenticated user
        db: Database session

    Returns:
        Success message
    """
    # Get application
    result = await db.execute(
        select(Application)
        .where(
            and_(
                Application.application_id == application_id,
                Application.user_id == current_user.user_id
            )
        )
    )
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    # Update notes
    application.notes = note_update.notes
    await db.flush()

    return {"status": "success", "message": "Notes updated"}


from datetime import datetime
