from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class ContextIssue(Base):
    """Clause 4.1: Internal/External Issues (PESTLE)"""
    __tablename__ = "context_issues"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False) # e.g., "Cloud Dependency"
    description = Column(Text, nullable=True)
    category = Column(String) # Internal / External
    pestle_category = Column(String) # Political, Economic, Social, Tech, Legal, Env
    impact = Column(String) # Low, Medium, High
    treatment = Column(Text) # How we address it
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class InterestedParty(Base):
    """Clause 4.2: Stakeholders"""
    __tablename__ = "interested_parties"

    id = Column(Integer, primary_key=True, index=True)
    stakeholder = Column(String, nullable=False) # e.g., "Customers"
    needs = Column(Text) # e.g., "Data Privacy"
    requirements = Column(Text) # e.g., "SOC 2 Report specific"
    compliance_mapping = Column(String) # Link to controls if needed
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ScopeDocument(Base):
    """Clause 4.3: ISMS Scope"""
    __tablename__ = "scope_documents"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text) # JSON or Markdown
    boundaries_physical = Column(Text)
    boundaries_logical = Column(Text)
    dependencies_json = Column(Text) # JSON for table
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
