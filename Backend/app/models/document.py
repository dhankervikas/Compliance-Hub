from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("policies.id"))
    content = Column(Text)
    tenant_id = Column(String, default="default_tenant", nullable=False, index=True)
    status = Column(String, default="approved")
    version = Column(String)
    approved_by = Column(String)
    approved_date = Column(DateTime, default=datetime.utcnow)
    
    # Optional: Path to the generated PDF
    pdf_path = Column(String, nullable=True)

    policy = relationship("Policy", back_populates="documents")
