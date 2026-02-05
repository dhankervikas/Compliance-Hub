from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models.process import Process, SubProcess, process_control_mapping
from app.models.control import Control

router = APIRouter(
    tags=["Processes"]
)

# --- Actionable Title Map (Vanta-Style) ---
ACTIONABLE_TITLES = {
    "A.5.1": "Define & Approve InfoSec Policies",
    "A.5.2": "Assign Information Security Roles",
    "A.5.3": "Segregate Conflicting Duties",
    "A.5.4": "Define Management Responsibilities",
    "A.5.5": "Establish Authority Contacts",
    "A.5.6": "Maintain Special Interest Group Contacts",
    "A.5.7": "Collect & Analyze Threat Intelligence",
    "A.5.8": "Integrate Security into Project Management",
    "A.5.9": "Inventory Information Assets",
    "A.5.10": "Enforce Acceptable Use Policy",
    "A.5.11": "Return Assets Upon Termination",
    "A.5.12": "Classify Information Sensitivity",
    "A.5.13": "Label Information Assets",
    "A.5.14": "Transfer Information Securely",
    "A.5.15": "Control Access Rights",
    "A.5.16": "Manage Identity Authentication",
    "A.5.17": "Verify Identity Guidelines",
    "A.5.18": "Manage Access Rights",
    "A.5.19": "Manage Information Security Risks",
    "A.5.20": "Address Security in Supplier Agreements",
    "A.5.21": "Manage ICT Supply Chain",
    "A.5.22": "Monitor & Review Supplier Services",
    "A.5.23": "Manage Cloud Services Security",
    "A.5.24": "Plan & Prepare for Incidents",
    "A.5.25": "Assess & Decide on Events",
    "A.5.26": "Respond to Information Security Incidents",
    "A.5.27": "Learn from Information Security Incidents",
    "A.5.28": "Collect Evidence",
    "A.5.29": "Plan for ICT Continuity",
    "A.5.30": "Verify ICT Readiness",
    "A.5.31": "Identify Legal Requirements",
    "A.5.32": "Protect Intellectual Property",
    "A.5.33": "Protect Records",
    "A.5.34": "Protect PII & Privacy",
    "A.5.35": "Review Independent Compliance",
    "A.5.36": "Review Compliance with Policies",
    "A.5.37": "Document Operating Procedures",
    "A.6.1": "Screen Candidates (Background Checks)",
    "A.6.2": "Agree on Terms of Employment",
    "A.6.3": "Train Employees on Security Awareness",
    "A.6.4": "Manage Disciplinary Process",
    "A.6.5": "Terminate or Change Employment",
    "A.6.6": "Sign Confidentiality Agreements",
    "A.6.7": "Secure Remote Working",
    "A.6.8": "Report Information Security Events",
    "A.7.1": "Secure Physical Perimeters",
    "A.7.2": "Secure Entry Controls",
    "A.7.3": "Secure Offices, Rooms & Facilities",
    "A.7.4": "Monitor Physical Security",
    "A.7.5": "Protect Against Physical Threats",
    "A.7.6": "Secure Working Areas",
    "A.7.7": "Clear Desk & Clear Screen Policy",
    "A.7.8": "Site & Equipment Siting",
    "A.7.9": "Secure Off-Site Assets",
    "A.7.10": "Secure Storage Media",
    "A.7.11": "Support Utilities Security",
    "A.7.12": "Cable Security",
    "A.7.13": "Maintain Equipment",
    "A.7.14": "Secure Disposal of Equipment",
    "A.8.1": "User Endpoint Devices",
    "A.8.2": "Privileged Access Rights",
    "A.8.3": "Information Access Restriction",
    "A.8.4": "Access to Source Code",
    "A.8.5": "Secure Authentication",
    "A.8.6": "Capacity Management",
    "A.8.7": "Malware Protection",
    "A.8.8": "Technical Vulnerability Management",
    "A.8.9": "Configuration Management",
    "A.8.10": "Information Deletion",
    "A.8.11": "Data Masking",
    "A.8.12": "Data Leakage Prevention",
    "A.8.13": "Information Backup",
    "A.8.14": "Redundancy of Info Processing",
    "A.8.15": "Logging",
    "A.8.16": "Monitoring Activities",
    "A.8.17": "Clock Synchronization",
    "A.8.18": "Use of Privileged Utility Programs",
    "A.8.19": "Installation of Software on Operational Systems",
    "A.8.20": "Network Security",
    "A.8.21": "Security of Network Services",
    "A.8.22": "Segregation of Networks",
    "A.8.23": "Web Filtering",
    "A.8.24": "Use of Cryptography",
    "A.8.25": "Secure Development Life Cycle",
    "A.8.26": "Application Security Requirements",
    "A.8.27": "Secure System Architecture",
    "A.8.28": "Secure Coding",
    "A.8.29": "Security Testing in Development",
    "A.8.30": "Outsourced Development Security",
    "A.8.31": "Separation of Dev/Test/Prod",
    "A.8.32": "Change Management",
    "A.8.33": "Test Information",
    "A.8.34": "Information Systems Audit Controls",
    
    # --- SOC 2 MAPPINGS (for Cross-Framework Sync) ---
    "CC1.1": "Define & Approve InfoSec Policies", # Matches A.5.1
    "CC1.2": "Assign Information Security Roles", # Matches A.5.2
    "CC1.3": "Define Management Responsibilities", # Matches A.5.4
    "CC1.4": "Screen Candidates (Background Checks)", # Matches A.6.1
    "CC1.5": "Train Employees on Security Awareness", # Matches A.6.3
    "CC2.1": "Inventory Information Assets", # Matches A.5.9
    "CC2.2": "Classify Information Sensitivity", # Matches A.5.12
    "CC2.3": "Control Access Rights", # Matches A.5.15
    "CC3.1": "Manage Identity Authentication", # Matches A.5.16
    "CC6.1": "Monitor Physical Security", # Matches A.7.4
    "CC6.6": "Secure Physical Perimeters" # Matches A.7.1
}

def get_actionable_title(control):
    return ACTIONABLE_TITLES.get(control.control_id, control.title)

# --- Pydantic Models ---
from app.api.auth import get_current_user
class Assignee(BaseModel):
    id: str
    name: str
    email: str
    initials: str

class ControlSummary(BaseModel):
    id: int
    control_id: str
    title: str
    actionable_title: str
    description: Optional[str] = None
    status: str
    framework_id: int
    category: Optional[str] = "Governance"
    automation_status: Optional[str] = "manual"
    shared_evidence_count: int = 0
    has_synced_evidence: bool = False
    assignee: Optional[Assignee] = None
    
    class Config:
        from_attributes = True

# ... (SubProcessBase, etc remain same)



class SubProcessBase(BaseModel):
    name: str
    description: Optional[str] = None

class SubProcessCreate(SubProcessBase):
    pass

class SubProcessResponse(SubProcessBase):
    id: int
    process_id: int
    mapped_controls_count: int = 0
    controls: List[ControlSummary] = []
    
    class Config:
        from_attributes = True

class ProcessBase(BaseModel):
    name: str
    description: Optional[str] = None
    framework_code: Optional[str] = "ISO27001"

class ProcessCreate(ProcessBase):
    sub_processes: List[SubProcessCreate] = []

class ProcessResponse(ProcessBase):
    id: int
    sub_processes: List[SubProcessResponse] = []
    stats: dict = {}
    
    class Config:
        from_attributes = True

class MappingRequest(BaseModel):
    control_ids: List[int]

# --- Endpoints ---

@router.post("/", response_model=ProcessResponse)
def create_process(process: ProcessCreate, db: Session = Depends(get_db)):
    db_process = Process(name=process.name, description=process.description, framework_code=process.framework_code)
    db.add(db_process)
    db.commit()
    db.refresh(db_process)
    
    for sp in process.sub_processes:
        db_sp = SubProcess(name=sp.name, description=sp.description, process_id=db_process.id)
        db.add(db_sp)
    
    db.commit()
    db.refresh(db_process)
    return db_process

@router.get("/", response_model=List[ProcessResponse])
def get_processes(
    framework_code: Optional[str] = None,
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    from app.services.process_service import ProcessService
    
    # 1. Resolve Framework Code (Default to ISO27001 if not provided, or handle None)
    target_fw = framework_code or "ISO27001"
    
    # 2. Get Data from Service
    # Structure: [{"id": 1, "name": "HR", "controls": [{...}]}]
    service_data = ProcessService.get_processes_with_controls(db, target_fw)
    
    response_processes = []
    
    for p_data in service_data:
        # Calculate Stats
        controls = p_data["controls"]
        stats = {
            "total": len(controls),
            "implemented": sum(1 for c in controls if c.get("status") == "implemented"),
            "in_progress": sum(1 for c in controls if c.get("status") == "in_progress"),
            "not_started": sum(1 for c in controls if c.get("status") == "not_started" or c.get("status") is None)
        }
        
        # Convert Controls to ControlSummary Schema
        # Note: Service returns dicts, need to map to Pydantic if stricter validation, or pass dicts if compatible.
        # Check ControlSummary definition requires assignee object, etc. 
        # For speed, we might need to rely on the Service returning fully compatible dicts OR simple mapping here.
        # The service I wrote returned simple dicts. I need to enhance the service or map here.
        # Let's map here for safety.
        
        enhanced_controls = []
        for c in controls:
             # Basic mapping
             enhanced_controls.append(ControlSummary(
                 id=c["id"],
                 control_id=c["control_id"],
                 title=c["title"],
                 actionable_title=c["title"], # Simplified for now
                 description=c["description"],
                 status=c.get("status", "not_started"),


                 framework_id=c.get("framework_id", 0), 
                 category=p_data["name"],
                 automation_status="manual",
                 shared_evidence_count=0,
                 has_synced_evidence=False,
                 assignee=c.get("assignee") 
             ))

        # Wrap in Synthetic SubProcess to satisfy Frontend
        # Frontend expects Process -> [SubProcess -> [Controls]]
        sp_res = SubProcessResponse(
            id=p_data["id"] * 1000, # Fake ID to avoid collision or fetch real if matched
            name=p_data["name"], # Use Process Name as SubProcess Name
            description=p_data["description"],
            process_id=p_data["id"],
            mapped_controls_count=len(enhanced_controls),
            controls=enhanced_controls
        )
        
        p_res = ProcessResponse(
            id=p_data["id"],
            name=p_data["name"],
            description=p_data["description"],
            framework_code=target_fw,
            sub_processes=[sp_res],
            stats=stats
        )
        response_processes.append(p_res)
        
    return response_processes

@router.post("/subprocess/{subprocess_id}/map-controls")
def map_controls_to_subprocess(subprocess_id: int, mapping: MappingRequest, db: Session = Depends(get_db)):
    """
    Link a list of Controls to a SubProcess.
    This defines that "This subprocess relies on these controls".
    """
    subprocess = db.query(SubProcess).filter(SubProcess.id == subprocess_id).first()
    if not subprocess:
        raise HTTPException(status_code=404, detail="SubProcess not found")
    
    # clear existing? or append? Let's assume append/merge for now, or replace.
    # Implementing REPLACE strategy for simplicity
    subprocess.controls = []
    
    controls = db.query(Control).filter(Control.id.in_(mapping.control_ids)).all()
    subprocess.controls.extend(controls)
    
    db.commit()
    return {"message": f"Mapped {len(controls)} controls to subprocess '{subprocess.name}'"}

@router.get("/subprocess/{subprocess_id}", response_model=SubProcessResponse)
def get_subprocess(subprocess_id: int, db: Session = Depends(get_db)):
    sp = db.query(SubProcess).filter(SubProcess.id == subprocess_id).first()
    if not sp:
        raise HTTPException(status_code=404, detail="SubProcess not found")
    sp.mapped_controls_count = len(sp.controls)
    return sp

@router.delete("/{process_id}", status_code=204)
def delete_process(process_id: int, db: Session = Depends(get_db)):
    """Delete a process and all its subprocesses"""
    process = db.query(Process).filter(Process.id == process_id).first()
    if not process:
        raise HTTPException(status_code=404, detail="Process not found")
    
    db.delete(process)
    db.commit()
    return None

@router.post("/{process_id}/subprocesses", response_model=SubProcessResponse)
def create_subprocess_for_process(process_id: int, subprocess: SubProcessCreate, db: Session = Depends(get_db)):
    """Add a subprocess to an existing process"""
    process = db.query(Process).filter(Process.id == process_id).first()
    if not process:
        raise HTTPException(status_code=404, detail="Process not found")
    
    db_sp = SubProcess(
        name=subprocess.name, 
        description=subprocess.description, 
        process_id=process_id
    )
    db.add(db_sp)
    db.commit()
    db.refresh(db_sp)
    return db_sp
