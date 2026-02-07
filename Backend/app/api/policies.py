from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models.policy import Policy
from app.api.auth import get_current_user

router = APIRouter(
    tags=["Policies"]
)

# --- Pydantic Models ---

class PolicyBase(BaseModel):
    name: str
    description: Optional[str] = None
    content: str
    folder: Optional[str] = "Uncategorized"
    status: Optional[str] = "Draft"
    owner: Optional[str] = "Compliance Team"
    linked_frameworks: Optional[str] = None

class PolicyCreate(PolicyBase):
    pass

class PolicyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    folder: Optional[str] = None
    status: Optional[str] = None # Draft, Review, Approved
    version: Optional[str] = None
    approval_date: Optional[datetime] = None
    approver: Optional[str] = None

class PolicyResponse(PolicyBase):
    id: int
    version: str
    updated_at: Optional[datetime]
    created_at: Optional[datetime]
    approval_date: Optional[datetime]
    approver: Optional[str] = None
    
    class Config:
        from_attributes = True

# --- Endpoints ---

@router.get("/", response_model=List[PolicyResponse])
def get_policies(folder: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Policy)
    if folder:
        query = query.filter(Policy.folder == folder)
    return query.all()

@router.post("/", response_model=PolicyResponse)
def create_policy(policy: PolicyCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_policy = Policy(
        name=policy.name,
        description=policy.description,
        content=policy.content,
        folder=policy.folder,
        status=policy.status,
        owner=policy.owner,
        linked_frameworks=policy.linked_frameworks,
        version="1.0"
    )
    db.add(db_policy)
    db.commit()
    db.refresh(db_policy)
    return db_policy

@router.get("/{policy_id}", response_model=PolicyResponse)
def get_policy(policy_id: int, db: Session = Depends(get_db)):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy

@router.put("/{policy_id}", response_model=PolicyResponse)
def update_policy(policy_id: int, policy_update: PolicyUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not db_policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    # Versioning Logic: If status changes to Approved, or content changes significantly, bump version?
    # For now, simplistic update. 
    # User wanted "Version History". This requires a separate table or complex logic.
    # MVP: We update the current row. 
    # To support versions: We should create a copy before update if status was Approved.
    
    if policy_update.status == "Approved" and db_policy.status != "Approved":
        policy_update.approval_date = datetime.now()
        policy_update.approver = current_user.email
    
    for key, value in policy_update.dict(exclude_unset=True).items():
        setattr(db_policy, key, value)
    
    db.commit()
    db.refresh(db_policy)
    return db_policy

@router.post("/{policy_id}/attest")
def attest_policy(policy_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Mock Attestation
    return {"message": "Policy attested successfully"}

@router.get("/export/auditor")
def export_policies_for_auditor(db: Session = Depends(get_db)):
    # Mock Export
    # In real app: Zip all approved policies by folder
    return {"message": "Export generated", "url": "https://mock-link.com/auditor-package.zip"}
