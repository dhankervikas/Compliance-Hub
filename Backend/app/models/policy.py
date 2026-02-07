from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Policy(Base):
    """
    Policy model for storing high-level compliance policies.
    """
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    tenant_id = Column(String, default="default_tenant", nullable=False, index=True)
    content = Column(Text, nullable=False) # Markdown/HTML content
    version = Column(String, default="1.0")
    status = Column(String, default="Draft") # Draft, Review, Approved
    folder = Column(String, default="Uncategorized") # Governance, People, Technology, Operations
    owner = Column(String, default="Compliance Team")
    linked_frameworks = Column(String, nullable=True) # e.g. "ISO 27001, SOC 2"
    
    # Template & Lifecycle Logic
    is_template = Column(Boolean, default=False)
    # Link to the Immutable Master Template (if this policy was cloned from one)
    master_template_id = Column(Integer, nullable=True) 
    parent_id = Column(Integer, nullable=True) # ID of the template this was cloned from (Legacy/Polymorphic)
    approval_date = Column(DateTime(timezone=True), nullable=True)
    approver = Column(String, nullable=True)
    mapped_controls = Column(Text, nullable=True) # JSON list of Control IDs e.g. ["A.5.15", "A.8.2"]
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    documents = relationship("Document", back_populates="policy")

    def __repr__(self):
        return f"<Policy {self.name}>"
