from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class ControlStatus(str, enum.Enum):
    """Status of control implementation"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    IMPLEMENTED = "implemented"

class AutomationStatus(str, enum.Enum):
    """Status of automated checks"""
    MANUAL = "manual"
    AUTOMATED = "automated"
    HYBRID = "hybrid"
    FAILED = "failed"

class Control(Base):
    """Control model for compliance controls"""
    
    __tablename__ = "controls"
    
    id = Column(Integer, primary_key=True, index=True)
    control_id = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    tenant_id = Column(String, default="default_tenant", nullable=False, index=True)
    
    # AI Generated Data (Persisted)
    ai_explanation = Column(Text, nullable=True) # Summary of clause
    ai_requirements_json = Column(Text, nullable=True) # JSON list of requirements
    
    framework_id = Column(Integer, ForeignKey("frameworks.id"), nullable=False)
    framework = relationship("Framework", back_populates="controls")
    
    # status = Column(Enum(ControlStatus), default=ControlStatus.NOT_STARTED)
    status = Column(String, default="not_started")
    owner = Column(String, nullable=True)
    implementation_notes = Column(Text, nullable=True)
    
    category = Column(String, nullable=True)
    priority = Column(String, default="medium")

    # SoA Fields (ISO 27001:2022 Clause 6.1.3d)
    is_applicable = Column(Boolean, default=True)
    justification = Column(Text, nullable=True) # Full text detail
    justification_reason = Column(String, nullable=True) # Structured Category (e.g. "Risk Assessment")
    implementation_method = Column(Text, nullable=True)
    
    # Process Approach Fields
    domain = Column(String, nullable=True, index=True) # e.g. "Access Management"
    classification = Column(String, default="MANUAL") # AUTO, MANUAL, HYBRID
    automation_status = Column(String, default="manual")
    last_automated_check = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Ownership & Assignment
    owner_id = Column(String, ForeignKey("people.id"), nullable=True) # Link to Person (HR Identity)
    department_id = Column(String, nullable=True) # Department ID/Name
    
    owner_rel = relationship("Person", back_populates="assigned_controls")
    
    evidence_items = relationship("Evidence", back_populates="control", cascade="all, delete-orphan")
     
    
    # Control mappings
    source_mappings = relationship(
        "ControlMapping",
        foreign_keys="[ControlMapping.source_control_id]",
        back_populates="source_control"
    )
    target_mappings = relationship(
        "ControlMapping", 
        foreign_keys="[ControlMapping.target_control_id]",
        back_populates="target_control"
    )

    assessments = relationship("Assessment", back_populates="control", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Control {self.control_id}: {self.title}>"

    @property
    def process_name(self):
        """Returns the name of the canonical process this control belongs to (via SubProcess)"""
        if self.sub_processes and len(self.sub_processes) > 0:
            # Assumes 1 mapped process (or takes the first one)
            return self.sub_processes[0].process.name
        return None

    @property
    def sub_process_name(self):
        """Returns the name of the sub-process (Policy Intent) this control belongs to"""
        if self.sub_processes and len(self.sub_processes) > 0:
            return self.sub_processes[0].name
        return None
  
