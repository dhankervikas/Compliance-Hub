from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class IntentFrameworkCrosswalk(Base):
    """
    The Data Bridge: Maps one Universal Intent to many Framework-specific controls.
    Example: Intent 'MFA' -> Framework 'ISO 27001', Control 'A.5.14'
    """
    __tablename__ = "intent_framework_crosswalk"
    
    id = Column(Integer, primary_key=True, index=True)
    intent_id = Column(Integer, ForeignKey("universal_intents.id"), nullable=False)
    framework_id = Column(String, nullable=False, index=True) # e.g. "ISO_27001", "SOC2"
    control_reference = Column(String, nullable=False) # e.g. "A.5.14", "CC6.1"
    
    # Relationship
    intent = relationship("UniversalIntent", back_populates="crosswalk_entries")

class StandardProcessOverlay(Base):
    """
    Dynamic Metadata: Maps Canonical Processes to Standard-specific labels.
    Example: Process 'HR Security' -> 'Annex A.6: People Controls' for ISO 27001.
    """
    __tablename__ = "standard_process_overlay"
    
    id = Column(Integer, primary_key=True, index=True)
    framework_id = Column(String, nullable=False, index=True) # e.g. "ISO_27001"
    process_name = Column(String, nullable=False) # e.g. "HR Security"
    external_label = Column(String, nullable=False) # e.g. "Annex A.6: People Controls"
    display_order = Column(Integer, default=0)
