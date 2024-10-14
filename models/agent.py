from sqlalchemy import Column, Integer, String, JSON, Float, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .base import Base


class Agent(Base):
    __tablename__ = 'agents'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    description = Column(String, nullable=False)
    speciality = Column(JSON, nullable=False)
    service = Column(String, nullable=False)
    rating = Column(Float, nullable=False)
    picture = Column(String, nullable=False)
    smb_id = Column(Integer, ForeignKey('smbs.id'))
    created_at = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc), nullable=False)

    issues = relationship('IssuesAgents', back_populates='agent')
    smb = relationship('SMB', back_populates='agents')
    appointments = relationship("Appointment", back_populates="agent")

    def __repr__(self):
        return f"<Agent(name={self.name}, email={self.email})>"
