from sqlalchemy import (
    Column, Integer, String, TIMESTAMP, ForeignKey, CheckConstraint
)
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from .base import Base  # Assuming you have a base class defined in your project

class VerificationRequest(Base):
    __tablename__ = 'verification_requests'

    id = Column(Integer, primary_key=True, autoincrement=True)
    visitor_id = Column(Integer, ForeignKey('visitors.id', ondelete='CASCADE'), nullable=False)
    type = Column(String(5), nullable=False)
    contact = Column(String(255), nullable=False)
    code = Column(String(10), nullable=False)
    expired_at = Column(TIMESTAMP, nullable=False)
    status = Column(String(10), nullable=False, default='open')
    created_at = Column(TIMESTAMP, nullable=False, default=lambda: datetime.now(timezone.utc))

    visitor = relationship("Visitor", back_populates="verification_requests")

    __table_args__ = (
        CheckConstraint("status IN ('open', 'completed')", name="verification_requests_status_check"),
        CheckConstraint("type IN ('email', 'phone')", name="verification_requests_type_check"),
    )
