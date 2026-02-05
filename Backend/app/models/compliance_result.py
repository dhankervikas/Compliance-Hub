from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.sql import func
from app.database import Base

class ComplianceResult(Base):
    """
    Stores the compliance status of a specific control for a tenant.
    Linked to controls via control_id (ISO ID).
    Includes encrypted evidence metadata.
    """
    __tablename__ = "compliance_results"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, default="default_tenant", nullable=False, index=True)
    
    control_id = Column(String, nullable=False, index=True) # e.g., "5.1", "A.5.1"
    status = Column(String, default="FAIL") # PASS, FAIL, WARNING, NOT_SCANNED
    
    # Encrypted Evidence Metadata (JSON String -> Encrypted)
    evidence_metadata = Column(Text, nullable=True) 
    
    last_scanned_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ComplianceResult {self.tenant_id} | {self.control_id}: {self.status}>"
