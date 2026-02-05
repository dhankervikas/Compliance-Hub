from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class ScopeJustification(Base):
    __tablename__ = "scope_justifications"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, nullable=False)
    
    # "ISO27001", "SOC2", "NIST_CSF"
    standard_type = Column(String, index=True, nullable=False)
    
    # "A.5.1", "CC6.1"
    criteria_id = Column(String, index=True, nullable=False)
    
    # "NOT_APPLICABLE", "OUT_OF_SCOPE", "PARTIALLY_APPLICABLE"
    reason_code = Column(String, nullable=False, default="NOT_APPLICABLE")
    
    justification_text = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
