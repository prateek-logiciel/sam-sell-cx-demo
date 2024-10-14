from sqlalchemy import Column, Integer, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import JSONB
from .base import Base

class SMBPreferences(Base):
    __tablename__ = 'smb_preferences'

    id = Column(Integer, primary_key=True)
    smb_id = Column(Integer, ForeignKey('smbs.id'), nullable=False)
    calendar_settings = Column(JSONB, nullable=True)
    storage_settings = Column(JSONB, nullable=True)
