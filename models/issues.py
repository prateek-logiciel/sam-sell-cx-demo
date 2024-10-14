from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class Issues(Base):
    __tablename__ = 'issues'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(10))
    description = Column(String(240))
    status = Column(String(10), default='OPEN')
    fk_visitor_id = Column(Integer, ForeignKey('visitors.id'))
    fk_smb_id = Column(Integer, ForeignKey('smbs.id'))
    visitor = relationship('Visitor', back_populates='issues')
    smb = relationship('SMB', back_populates='issues')
    issues_agents = relationship('IssuesAgents', back_populates='issue')
