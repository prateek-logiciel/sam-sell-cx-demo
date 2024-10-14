from sqlalchemy import Table, Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from .base import Base


class IssuesAgents(Base):
    __tablename__ = 'issues_agents'
    
    issue_id = Column(Integer, ForeignKey('issues.id'), primary_key=True)
    agent_id = Column(Integer, ForeignKey('agents.id'), primary_key=True)
    status = Column('status', String(10), nullable=True)
    issue = relationship('Issues', back_populates='issues_agents')
    agent = relationship('Agent', back_populates='issues')
