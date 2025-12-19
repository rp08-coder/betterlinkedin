"""
Job endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.job import Job, JobQueue
from app.models.application import Application, SwipeHistory, ApplicationStatus
from app.schemas.job import JobResponse, JobQueueResponse, SwipeAction

router = APIRouter()


@router.get("/queue", response_model=List[JobQueueResponse])
async def get_job_queue(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get personalized job queue for current user

    Args:
        limit: Maximum number of jobs to return
        current_user: Authenticated user
        db: Database session

    Returns:
        List of jobs in user's queue
    """
    # Get unshown jobs from queue, ordered by relevance score
    result = await db.execute(
        select(JobQueue)
        .join(Job)
        .where(
            and_(
                JobQueue.user_id == current_user.user_id,
                JobQueue.shown == False,  # noqa: E712
                Job.is_active == True  # noqa: E712
            )
        )
        .order_by(desc(JobQueue.relevance_score))
        .limit(limit)
    )

    queue_items = result.scalars().all()

    # Convert to response format
    response = []
    for item in queue_items:
        job_response = JobResponse(
            job_id=item.job.job_id,
            source_url=item.job.source_url,
            company_name=item.job.company_name,
            company_logo_url=item.job.company_logo_url,
            job_title=item.job.job_title,
            description=item.job.description,
            requirements=item.job.requirements,
            job_category=item.job.job_category,
            sector=item.job.sector,
            location=item.job.location,
            date_posted=item.job.date_posted,
            is_active=item.job.is_active,
            application_url=item.job.application_url,
            application_platform=item.job.application_platform,
            custom_questions=item.job.custom_questions,
            relevance_score=item.relevance_score
        )

        response.append(JobQueueResponse(
            queue_id=item.queue_id,
            job=job_response,
            relevance_score=item.relevance_score,
            date_added=item.date_added
        ))

    return response


@router.post("/swipe", status_code=status.HTTP_200_OK)
async def swipe_job(
    swipe: SwipeAction,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Record a swipe action on a job

    Args:
        swipe: Swipe action data (job_id, direction)
        current_user: Authenticated user
        db: Database session

    Returns:
        Success message
    """
    # Verify job exists and is in user's queue
    result = await db.execute(
        select(JobQueue)
        .where(
            and_(
                JobQueue.user_id == current_user.user_id,
                JobQueue.job_id == swipe.job_id
            )
        )
    )
    queue_item = result.scalar_one_or_none()

    if not queue_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found in queue"
        )

    # Mark job as shown
    queue_item.shown = True

    # Record swipe history
    swipe_history = SwipeHistory(
        user_id=current_user.user_id,
        job_id=swipe.job_id,
        direction=swipe.action,
        timestamp=swipe.timestamp
    )
    db.add(swipe_history)

    # Handle swipe action
    if swipe.action == "left":
        # Reject - add to rejected list
        if current_user.rejected_job_urls is None:
            current_user.rejected_job_urls = []

        job_result = await db.execute(
            select(Job).where(Job.job_id == swipe.job_id)
        )
        job = job_result.scalar_one()

        if job.source_url not in current_user.rejected_job_urls:
            current_user.rejected_job_urls = current_user.rejected_job_urls + [job.source_url]

    elif swipe.action == "right":
        # Apply - create application record
        application = Application(
            user_id=current_user.user_id,
            job_id=swipe.job_id,
            status=ApplicationStatus.OUTSTANDING,  # Will be auto-applied
            date_swiped=swipe.timestamp
        )
        db.add(application)

    await db.flush()

    return {"status": "success", "message": f"Swiped {swipe.action} on job"}


@router.post("/undo", response_model=JobQueueResponse)
async def undo_swipe(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Undo the last swipe action

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        Restored job queue item
    """
    # Get most recent swipe that hasn't been undone
    result = await db.execute(
        select(SwipeHistory)
        .where(
            and_(
                SwipeHistory.user_id == current_user.user_id,
                SwipeHistory.undone == False  # noqa: E712
            )
        )
        .order_by(desc(SwipeHistory.timestamp))
        .limit(1)
    )
    last_swipe = result.scalar_one_or_none()

    if not last_swipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No recent swipe to undo"
        )

    # Mark swipe as undone
    last_swipe.undone = True
    last_swipe.undo_timestamp = datetime.utcnow()

    # Get the job queue item
    queue_result = await db.execute(
        select(JobQueue)
        .where(
            and_(
                JobQueue.user_id == current_user.user_id,
                JobQueue.job_id == last_swipe.job_id
            )
        )
    )
    queue_item = queue_result.scalar_one()

    # Mark as not shown
    queue_item.shown = False

    # Handle undo based on direction
    if last_swipe.direction == "left":
        # Remove from rejected list
        job_result = await db.execute(
            select(Job).where(Job.job_id == last_swipe.job_id)
        )
        job = job_result.scalar_one()

        if current_user.rejected_job_urls and job.source_url in current_user.rejected_job_urls:
            current_user.rejected_job_urls = [
                url for url in current_user.rejected_job_urls if url != job.source_url
            ]

    elif last_swipe.direction == "right":
        # Delete application
        app_result = await db.execute(
            select(Application)
            .where(
                and_(
                    Application.user_id == current_user.user_id,
                    Application.job_id == last_swipe.job_id
                )
            )
            .order_by(desc(Application.date_swiped))
            .limit(1)
        )
        application = app_result.scalar_one_or_none()

        if application:
            await db.delete(application)

    await db.flush()
    await db.refresh(queue_item)

    # Build response
    job_response = JobResponse(
        job_id=queue_item.job.job_id,
        source_url=queue_item.job.source_url,
        company_name=queue_item.job.company_name,
        company_logo_url=queue_item.job.company_logo_url,
        job_title=queue_item.job.job_title,
        description=queue_item.job.description,
        requirements=queue_item.job.requirements,
        job_category=queue_item.job.job_category,
        sector=queue_item.job.sector,
        location=queue_item.job.location,
        date_posted=queue_item.job.date_posted,
        is_active=queue_item.job.is_active,
        application_url=queue_item.job.application_url,
        application_platform=queue_item.job.application_platform,
        custom_questions=queue_item.job.custom_questions,
        relevance_score=queue_item.relevance_score
    )

    return JobQueueResponse(
        queue_id=queue_item.queue_id,
        job=job_response,
        relevance_score=queue_item.relevance_score,
        date_added=queue_item.date_added
    )
