"""
Job schemas for request/response validation
"""

from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class CustomQuestion(BaseModel):
    """Custom application question schema"""
    id: str
    question: str
    question_type: str  # "text", "textarea", "select", etc.
    required: bool = True


class JobResponse(BaseModel):
    """Job response schema"""
    job_id: UUID
    source_url: str
    company_name: str
    company_logo_url: Optional[str] = None
    job_title: str
    description: str
    requirements: str
    job_category: str
    sector: str
    location: str
    date_posted: Optional[datetime] = None
    is_active: bool
    application_url: str
    application_platform: str
    custom_questions: Optional[List[CustomQuestion]] = None
    relevance_score: Optional[int] = None

    class Config:
        from_attributes = True


class JobQueueResponse(BaseModel):
    """Job queue item response schema"""
    queue_id: UUID
    job: JobResponse
    relevance_score: int
    date_added: datetime

    class Config:
        from_attributes = True


class SwipeAction(BaseModel):
    """Swipe action request schema"""
    job_id: UUID
    action: str  # "left" or "right"
    timestamp: datetime


class JobCreate(BaseModel):
    """Schema for creating a job (scraping service)"""
    source_url: str
    vc_firm: Optional[str] = None
    company_name: str
    company_logo_url: Optional[str] = None
    job_title: str
    description: str
    requirements: str
    job_category: str
    sector: str
    location: str
    date_posted: Optional[datetime] = None
    application_url: str
    application_platform: str
    custom_questions: Optional[List[Dict[str, Any]]] = None
