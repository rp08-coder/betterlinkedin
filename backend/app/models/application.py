"""
Application model
"""

from sqlalchemy import Column, String, Text, DateTime, JSON, ForeignKey, Enum, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from app.core.database import Base


class ApplicationStatus(str, enum.Enum):
    """Application status enum"""
    OUTSTANDING = "outstanding"
    APPLIED = "applied"
    INTERVIEWING = "interviewing"
    OFFERED = "offered"
    REJECTED = "rejected"


class Application(Base):
    """Application tracking model"""

    __tablename__ = "applications"

    # Primary key
    application_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.job_id"), nullable=False)

    # Status
    status = Column(
        Enum(ApplicationStatus),
        default=ApplicationStatus.OUTSTANDING,
        index=True,
        nullable=False
    )

    # Dates
    date_swiped = Column(DateTime(timezone=True), server_default=func.now())
    date_applied = Column(DateTime(timezone=True), nullable=True)

    # Application content
    custom_responses = Column(JSON, nullable=True)  # Responses to custom questions
    cover_letter = Column(Text, nullable=True)

    # Tracking
    notes = Column(Text, nullable=True)
    interview_stage = Column(String, nullable=True)
    offer_details = Column(JSON, nullable=True)

    # Relationships
    job = relationship("Job")

    # Indexes for faster queries
    __table_args__ = (
        Index('idx_user_status', 'user_id', 'status'),
        Index('idx_user_date', 'user_id', 'date_swiped'),
    )

    def __repr__(self):
        return f"<Application user={self.user_id} job={self.job_id} status={self.status}>"


class SwipeHistory(Base):
    """
    Track all swipes for undo functionality and analytics.
    Separate from Application to track rejections as well.
    """

    __tablename__ = "swipe_history"

    # Primary key
    swipe_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.job_id"), nullable=False)

    # Swipe details
    direction = Column(String, nullable=False)  # "left" or "right"
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Undo tracking
    undone = Column(Boolean, default=False, nullable=False)
    undo_timestamp = Column(DateTime(timezone=True), nullable=True)

    # Indexes
    __table_args__ = (
        Index('idx_user_timestamp', 'user_id', 'timestamp'),
    )

    def __repr__(self):
        return f"<SwipeHistory user={self.user_id} direction={self.direction}>"
