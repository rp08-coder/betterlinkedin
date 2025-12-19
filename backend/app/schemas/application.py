"""
Application schemas for request/response validation
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from app.models.application import ApplicationStatus
from app.schemas.job import JobResponse


class CustomResponse(BaseModel):
    """Custom question response schema"""
    id: str
    question_id: str
    response: str


class OfferDetails(BaseModel):
    """Offer details schema"""
    salary: Optional[int] = None
    start_date: Optional[datetime] = None
    equity: Optional[str] = None
    benefits: Optional[str] = None
    other_details: Optional[str] = None


class ApplicationResponse(BaseModel):
    """Application response schema"""
    application_id: UUID
    user_id: UUID
    job: JobResponse
    status: ApplicationStatus
    date_swiped: datetime
    date_applied: Optional[datetime] = None
    custom_responses: Optional[List[CustomResponse]] = None
    cover_letter: Optional[str] = None
    notes: Optional[str] = None
    interview_stage: Optional[str] = None
    offer_details: Optional[OfferDetails] = None

    class Config:
        from_attributes = True


class ApplicationStatusUpdate(BaseModel):
    """Schema for updating application status"""
    status: ApplicationStatus


class CustomResponsesSubmit(BaseModel):
    """Schema for submitting custom question responses"""
    responses: List[CustomResponse]


class ApplicationNoteUpdate(BaseModel):
    """Schema for updating application notes"""
    notes: str
