from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Assessment(Base):
    """
    Assessment model for storing AI-driven compliance analysis results.
    """
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    control_id = Column(Integer, ForeignKey("controls.id"), nullable=False)
    tenant_id = Column(String, default="default_tenant", nullable=False, index=True)
    
    # AI Analysis Results
    compliance_score = Column(Integer, nullable=True) # 0-100
    gaps = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    
    assessed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    control = relationship("Control", back_populates="assessments")

    def __repr__(self):
        return f"<Assessment ControlID={self.control_id} Score={self.compliance_score}>"
