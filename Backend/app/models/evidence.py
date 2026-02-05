from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Evidence(Base):
    """Evidence model for documents"""
    
    __tablename__ = "evidence"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(BigInteger, nullable=True)
    file_type = Column(String, nullable=True)
    tenant_id = Column(String, default="default_tenant", nullable=False, index=True)
    master_intent_id = Column(String, nullable=True, index=True) # Antigravity Directive 3
    
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    control_id = Column(Integer, ForeignKey("controls.id"), nullable=False)
    control = relationship("Control", back_populates="evidence_items")
    
    uploaded_by = Column(String, nullable=True)
    collection_date = Column(DateTime(timezone=True), nullable=True)
    tags = Column(String, nullable=True)
    
    # Validation Fields
    status = Column(String, default="pending") # pending, valid, outdated, rejected
    validation_source = Column(String, default="manual") # manual, automated_agent, api

    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Evidence {self.filename}>"