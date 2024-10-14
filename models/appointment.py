from sqlalchemy import Column, Integer, DateTime, Text, CheckConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Appointment(Base):
    __tablename__ = 'appointments'

    id = Column(Integer, primary_key=True)    
    smb_id = Column(Integer, ForeignKey('smbs.id'), nullable=False)
    agent_id = Column(Integer, ForeignKey('agents.id'), nullable=False)
    visitor_id = Column(Integer, ForeignKey('visitors.id'), nullable=False)
    calendar = Column(JSONB, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    summary = Column(Text, nullable=True)
    attendees = Column(JSONB, nullable=True)

    # Relationships
    smb = relationship("SMB", back_populates="appointments")
    agent = relationship("Agent", back_populates="appointments")
    visitor = relationship("Visitor", back_populates="appointments")

    __table_args__ = (
        CheckConstraint("(calendar ? 'source') AND (calendar ? 'id') AND (calendar ? 'event')",
                        name='check_calendar_json'),
        {'postgresql_using': 'btree'}  # This is the default, but explicitly stated for clarity
    )

    def __repr__(self):
        return f"<Appointment(id={self.id}, smb_id={self.smb_id}, start_time={self.start_time})>"