from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Address(Base):
    __tablename__ = 'address'

    id = Column(Integer, primary_key=True)
    visitor_id = Column(Integer, ForeignKey('visitors.id'), nullable=False)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    zipcode = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    is_primary = Column(Boolean, default=False, nullable=False)
    created_at = Column(TIMESTAMP, default=func.now(), nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)

    # Define the relationship with the 'visitors' table
    visitor = relationship("Visitor", back_populates="addresses")
