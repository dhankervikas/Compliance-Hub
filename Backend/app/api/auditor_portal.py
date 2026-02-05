from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.audit_assessment import AuditAssessment
from app.api.deps import verify_tenant

router = APIRouter(
    prefix="/auditor",
    tags=["auditor"]
)

# --- Schemas ---
class AssessmentCreate(BaseModel):
    framework_id: str
    control_id: str
    status: str  # COMPLIANT, NON_CONFORMITY, OFI, PENDING
    remarks: Optional[str] = None
    evidence_request_flag: bool = False

class AssessmentResponse(AssessmentCreate):
    id: str
    auditor_id: str
    created_at: str
    
    class Config:
        from_attributes = True

# --- Endpoints ---



@router.get("/assessments", response_model=List[AssessmentResponse])
def get_assessments(
    request: "Request",
    framework_id: str = Query(..., description="Framework ID (e.g., ISO27001, SOC2)"),
    db: Session = Depends(get_db)
):
    """
    Fetch all assessments for the current tenant and specified framework.
    Strictly filters by tenant_id from the session context (RLS).
    """
    tenant_id = request.state.tenant_id
    results = db.query(AuditAssessment).filter(
        AuditAssessment.tenant_id == tenant_id,
        AuditAssessment.framework_id == framework_id
    ).all()
    return results

@router.get("/assessments/list")
def list_assessments(
    request: "Request",
    framework_id: str,
    db: Session = Depends(get_db)
):
    tenant_id = request.state.tenant_id
    results = db.query(AuditAssessment).filter(
        AuditAssessment.tenant_id == tenant_id,
        AuditAssessment.framework_id == framework_id
    ).all()
    return results

@router.post("/assessments")
def create_or_update_assessment(
    request: "Request",
    payload: AssessmentCreate,
    db: Session = Depends(get_db)
):
    tenant_id = request.state.tenant_id
    user_id = request.state.user_id # Assuming auth middleware sets this
    
    if not user_id:
        # Fallback for dev/mock
        user_id = "auditor-01"

    # Upsert Logic
    existing = db.query(AuditAssessment).filter(
        AuditAssessment.tenant_id == tenant_id,
        AuditAssessment.framework_id == payload.framework_id,
        AuditAssessment.control_id == payload.control_id
    ).first()

    if existing:
        existing.status = payload.status
        existing.remarks = payload.remarks
        existing.evidence_request_flag = payload.evidence_request_flag
        existing.auditor_id = user_id
    else:
        new_assessment = AuditAssessment(
            tenant_id=tenant_id,
            framework_id=payload.framework_id,
            control_id=payload.control_id,
            auditor_id=user_id,
            status=payload.status,
            remarks=payload.remarks,
            evidence_request_flag=payload.evidence_request_flag
        )
        db.add(new_assessment)
    
    db.commit()
    return {"status": "success", "action": "updated" if existing else "created"}
