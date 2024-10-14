from sqlalchemy import Column, Integer, String, JSON, TIMESTAMP, ForeignKey, CheckConstraint, Boolean
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from .base import Base

class Visitor(Base):
    __tablename__ = 'visitors'

    id = Column(Integer, primary_key=True)
    session_id = Column(String, nullable=False)
    smb_id = Column(Integer, ForeignKey('smbs.id'), nullable=True)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    source = Column(String(5), default='ew', nullable=False)
    ip_address = Column(String(45), nullable=True)
    location = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False)
    browser_info = Column(JSON, nullable=True)
    is_email_verified = Column(Boolean, default=False, nullable=False)
    is_customer = Column(Boolean, default=False, nullable=False)
    is_phone_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(TIMESTAMP, nullable=True)
    issues = relationship('Issues', back_populates='visitor')
    addresses = relationship('Address', back_populates='visitor')
    appointments = relationship("Appointment", back_populates="visitor")

    __table_args__ = (
        CheckConstraint(status.in_(['active', 'inactive']), name='check_status'),
    )
