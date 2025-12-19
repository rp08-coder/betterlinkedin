"""
User model
"""

from sqlalchemy import Column, String, Integer, Boolean, ARRAY, JSON, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.database import Base


class User(Base):
    """User model for authentication and profile"""

    __tablename__ = "users"

    # Primary key
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Authentication
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

    # Basic profile
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    city = Column(String, nullable=True)
    phone = Column(String, nullable=True)

    # Resume
    resume_url = Column(String, nullable=True)

    # Preferences
    sectors = Column(ARRAY(String), default=list, nullable=False)
    job_types = Column(ARRAY(String), default=list, nullable=False)
    skills = Column(ARRAY(String), default=list, nullable=False)

    # Experience
    years_experience = Column(Integer, default=0, nullable=False)

    # Salary
    salary_min = Column(Integer, nullable=True)

    # Demographics (optional)
    demographics = Column(JSON, nullable=True)

    # Rejected jobs (list of job URLs)
    rejected_job_urls = Column(ARRAY(String), default=list, nullable=False)

    # Settings
    daily_application_limit = Column(Integer, default=10, nullable=False)
    notification_preferences = Column(JSON, default=dict, nullable=False)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_active = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<User {self.email}>"
