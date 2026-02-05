from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base

class AuditAssessment(Base):
    __tablename__ = "audit_assessments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, nullable=False, index=True) # RLS
    
    # Framework Isolation
    framework_id = Column(String, nullable=False, index=True) # e.g., 'ISO27001', 'SOC2'
    
    # Target (Control or Intent)
    control_id = Column(String, nullable=False, index=True) 
    
    # Assessment Data
    auditor_id = Column(String, nullable=False) # User ID of the auditor
    status = Column(String, default="PENDING") # PENDING, COMPLIANT, NON_CONFORMITY, OFI
    remarks = Column(Text, nullable=True)
    evidence_request_flag = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
