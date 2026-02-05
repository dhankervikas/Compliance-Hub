
from fastapi import APIRouter, HTTPException
from typing import Optional, List
from pydantic import BaseModel
from app.services.data_adapter import DataSourceAdapter
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends
from app.database import get_db

router = APIRouter(
    tags=["audits"]
)

adapter = DataSourceAdapter()

# Schemas
class AuditInitiationRequest(BaseModel):
    type: str # INTERNAL, EXTERNAL
    audit_period: Optional[str] = None
    risk_area: Optional[str] = None
    auditor_name: Optional[str] = None
    certification_body: Optional[str] = None
    stage: Optional[str] = None

class EvidenceReviewRequest(BaseModel):
    status: str # VERIFIED, NON_CONFORMITY, NEEDS_CLARIFICATION
    comment: Optional[str] = None

@router.post("/initiate")
def initiate_audit(request: AuditInitiationRequest):
    # In a real app, this would create an Audit Record in DB
    # For now, we just acknowledge receipt for the mock wizard
    return {
        "status": "success", 
        "message": f"Audit of type {request.type} initiated.",
        "audit_id": "AUD-2026-001"
    }

@router.get("/evidence")
def get_evidence(db: Session = Depends(get_db)):
    print(f"[DEBUG] GET /evidence called. DB Session: {db}")
    result = adapter.get_all_evidence(db)
    print(f"[DEBUG] GET /evidence returning {len(result)} items")
    return result

@router.post("/evidence/{evidence_id}/review")
def review_evidence(evidence_id: str, request: EvidenceReviewRequest, db: Session = Depends(get_db)):
    # Custom Validation: Rejection requires comment
    if request.status in ["NON_CONFORMITY", "NEEDS_CLARIFICATION"] and not request.comment:
        raise HTTPException(status_code=400, detail="Comment is mandatory for this status.")
    
    # Note: Adapter update method primarily works on JSON for now, but if we move to DB 
    # it would need 'db' session. Mock update doesn't use DB.
    success = adapter.update_evidence_status(evidence_id, request.status, request.comment)
    if not success:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    return {"status": "success", "new_state": request.status}

@router.get("/stats")
def get_audit_stats(db: Session = Depends(get_db)):
    # Helper to calculate stats for dashboard
    data = adapter.get_all_evidence(db)
    stats = {
        "total": len(data),
        "verified": len([x for x in data if x['status'] == 'VERIFIED']),
        "pending": len([x for x in data if x['status'] == 'PENDING']),
        "non_conformity": len([x for x in data if x['status'] == 'NON_CONFORMITY']),
        "needs_clarification": len([x for x in data if x['status'] == 'NEEDS_CLARIFICATION'])
    }
    return stats
