"""
Job models
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, JSON, ForeignKey, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Job(Base):
    """Job posting model"""

    __tablename__ = "jobs"

    # Primary key
    job_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Job source
    source_url = Column(String, unique=True, index=True, nullable=False)
    vc_firm = Column(String, nullable=True)  # Which VC firm portfolio

    # Company info
    company_name = Column(String, index=True, nullable=False)
    company_logo_url = Column(String, nullable=True)

    # Job details
    job_title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    requirements = Column(Text, nullable=False)

    # Classification
    job_category = Column(String, index=True, nullable=False)  # e.g., "Engineering"
    sector = Column(String, index=True, nullable=False)  # e.g., "Fintech"

    # Location
    location = Column(String, index=True, nullable=False)

    # Dates
    date_scraped = Column(DateTime(timezone=True), server_default=func.now())
    date_posted = Column(DateTime(timezone=True), nullable=True)

    # Status
    is_active = Column(Boolean, default=True, index=True, nullable=False)

    # Application info
    application_url = Column(String, nullable=False)
    application_platform = Column(String, nullable=False)  # "greenhouse", "lever", etc.
    custom_questions = Column(JSON, nullable=True)  # Array of question objects

    # Indexes for faster queries
    __table_args__ = (
        Index('idx_active_category_sector', 'is_active', 'job_category', 'sector'),
        Index('idx_company_active', 'company_name', 'is_active'),
    )

    def __repr__(self):
        return f"<Job {self.job_title} at {self.company_name}>"


class JobQueue(Base):
    """
    User-specific job queue with relevance scoring.
    Jobs are matched to users and added to their queue.
    """

    __tablename__ = "user_job_queue"

    # Primary key
    queue_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.job_id"), nullable=False)

    # Matching
    relevance_score = Column(Integer, nullable=False)  # 0-100

    # Status
    date_added = Column(DateTime(timezone=True), server_default=func.now())
    shown = Column(Boolean, default=False, nullable=False)  # Has user seen this job?

    # Relationships
    job = relationship("Job")

    # Indexes
    __table_args__ = (
        Index('idx_user_shown', 'user_id', 'shown'),
        Index('idx_user_score', 'user_id', 'relevance_score'),
    )

    def __repr__(self):
        return f"<JobQueue user={self.user_id} job={self.job_id} score={self.relevance_score}>"
