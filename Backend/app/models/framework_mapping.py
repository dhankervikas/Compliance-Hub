from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class FrameworkMapping(Base):
    """
    Maps a CommonControl to a specific Framework Control ID.
    Example: CommonControl(Encryption) -> ISO(A.5.11), SOC2(CC6.1)
    """
    __tablename__ = "framework_mappings"

    id = Column(Integer, primary_key=True, index=True)
    
    common_control_id = Column(Integer, ForeignKey("common_controls.id"), nullable=False, index=True)
    
    # Target Control Target
    # storing control_id (string) instead of FK to avoid complex circular deps with Control table 
    # and because Control ID is the semantic key.
    # We also store framework_id to help filtering without joining.
    control_id = Column(String, nullable=False, index=True) # e.g., "A.5.11"
    framework_id = Column(Integer, ForeignKey("frameworks.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    common_control = relationship("CommonControl", backref="mappings")
    framework = relationship("Framework")

    def __repr__(self):
        return f"<Mapping {self.common_control_id} -> {self.control_id} (FW: {self.framework_id})>"
