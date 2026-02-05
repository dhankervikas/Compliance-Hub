from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.models.control import ControlStatus


class ControlBase(BaseModel):
    control_id: str
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    domain: Optional[str] = None # Added for Business Process Mapping
    priority: str = "medium"
    implementation_notes: Optional[str] = None
    classification: Optional[str] = "MANUAL" # AUTO, MANUAL, HYBRID
    
    # Process View Fields
    process_name: Optional[str] = None
    sub_process_name: Optional[str] = None
    
    # SoA Fields
    is_applicable: bool = True
    justification: Optional[str] = None
    justification_reason: Optional[str] = None
    implementation_method: Optional[str] = None


class ControlCreate(ControlBase):
    framework_id: int
    owner: Optional[str] = None
    status: ControlStatus = ControlStatus.NOT_STARTED


class ControlUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ControlStatus] = None
    owner: Optional[str] = None
    implementation_notes: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    classification: Optional[str] = None


class Control(ControlBase):
    id: int
    framework_id: int
    status: str # Relaxed from ControlStatus to prevent validation errors with DB strings
    owner: Optional[str] = None
    implementation_notes: Optional[str] = None
    automation_status: Optional[str] = "manual"
    updated_at: Optional[datetime] = None
    
    # INCLUDE EVIDENCE FOR SYNC VISIBILITY
    # INCLUDE EVIDENCE FOR SYNC VISIBILITY
    evidence_items: List['Evidence'] = []
    
    class Config:
        from_attributes = True

from app.schemas.evidence import Evidence
Control.update_forward_refs()


class ControlWithFramework(Control):
    framework_name: str
    framework_code: str

# NEW: Schema for SoA Updates
class SoAUpdate(BaseModel):
    control_id: str
    is_applicable: bool
    justification: Optional[str] = None
    justification_reason: Optional[str] = None
    implementation_method: Optional[str] = None