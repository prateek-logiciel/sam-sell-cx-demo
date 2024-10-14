from sqlalchemy import Column, Integer, String, DateTime
from .base import Base

class PasswordResetToken(Base):
    __tablename__ = 'password_reset_tokens'

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    token = Column(String, nullable=False, unique=True)
    expiration_time = Column(DateTime, nullable=False)