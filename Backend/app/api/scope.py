from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.database import get_db
from app.models.scope_justification import ScopeJustification
from app.api.auth import get_current_user
from app.models.user import User

router = APIRouter()

# --- Pydantic Schemas ---
class ScopeJustificationCreate(BaseModel):
    standard_type: str # ISO27001, SOC2, NIST_CSF
    criteria_id: str
    reason_code: str
    justification_text: Optional[str] = None

class ScopeJustificationRead(ScopeJustificationCreate):
    id: int
    tenant_id: str

    class Config:
        orm_mode = True

# --- API Endpoints ---

@router.get("/justifications", response_model=List[ScopeJustificationRead])
def get_scope_justifications(
    standard_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Resolve Tenant UUID
    from app.models.tenant import Tenant
    tenant = db.query(Tenant).filter(Tenant.slug == current_user.tenant_id).first()
    tenant_uuid = tenant.internal_tenant_id if tenant else current_user.tenant_id

    query = db.query(ScopeJustification).filter(ScopeJustification.tenant_id == tenant_uuid)
    
    if standard_type:
        query = query.filter(ScopeJustification.standard_type == standard_type)
        
    return query.all()

@router.post("/justifications", response_model=ScopeJustificationRead)
def create_or_update_justification(
    payload: ScopeJustificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Resolve Tenant UUID
    from app.models.tenant import Tenant
    tenant = db.query(Tenant).filter(Tenant.slug == current_user.tenant_id).first()
    tenant_uuid = tenant.internal_tenant_id if tenant else current_user.tenant_id

    # Check for existing record
    existing = db.query(ScopeJustification).filter(
        ScopeJustification.tenant_id == tenant_uuid,
        ScopeJustification.standard_type == payload.standard_type,
        ScopeJustification.criteria_id == payload.criteria_id
    ).first()

    if existing:
        existing.reason_code = payload.reason_code
        existing.justification_text = payload.justification_text
        db.commit()
        db.refresh(existing)
        return existing
    else:
        new_record = ScopeJustification(
            tenant_id=tenant_uuid,
            standard_type=payload.standard_type,
            criteria_id=payload.criteria_id,
            reason_code=payload.reason_code,
            justification_text=payload.justification_text
        )
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return new_record

@router.delete("/justifications/{criteria_id}")
def delete_justification(
    criteria_id: str,
    standard_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Resolve Tenant UUID
    from app.models.tenant import Tenant
    tenant = db.query(Tenant).filter(Tenant.slug == current_user.tenant_id).first()
    tenant_uuid = tenant.internal_tenant_id if tenant else current_user.tenant_id

    # Strictly filter by standard type to prevent accidental deletion across standards if IDs clash (unlikely but safe)
    record = db.query(ScopeJustification).filter(
        ScopeJustification.tenant_id == tenant_uuid,
        ScopeJustification.criteria_id == criteria_id,
        ScopeJustification.standard_type == standard_type
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Justification not found")

    db.delete(record)
    db.commit()
    return {"status": "success", "message": "Justification removed"}
