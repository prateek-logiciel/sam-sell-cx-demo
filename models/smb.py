from sqlalchemy import Column, Integer, String, TIMESTAMP, CheckConstraint
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from .base import Base

class SMB(Base):
    __tablename__ = 'smbs'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    website = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False)
    refresh_token = Column(String(512), nullable=True)
    access_token = Column(String(512), nullable=True)
    created_at = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(TIMESTAMP, nullable=True)

    issues = relationship('Issues', back_populates='smb')
    agents = relationship('Agent', back_populates='smb')
    appointments = relationship("Appointment", back_populates="smb")

    __table_args__ = (
        CheckConstraint(status.in_(['active', 'inactive']), name='check_status'),
    )
