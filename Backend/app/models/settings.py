from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class ComplianceSettings(Base):
    __tablename__ = "compliance_settings"

    # We use section_key as the Primary Key for simplicity (one row per section)
    # e.g., 'org_profile', 'tech_stack'
    section_key = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, primary_key=True, index=True, default="default_tenant")
    
    # Stores the full JSON blob for that section
    content = Column(JSON, nullable=False, default={})
    
    # Metadata
    completeness_score = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String, nullable=True) # Optional User ID
