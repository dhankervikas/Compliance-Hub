from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, List, Any

from app.database import get_db
from app.models.compliance_result import ComplianceResult
from app.models.control import Control
from app.models.tenant import Tenant
from app.models.tenant_framework import TenantFramework
from app.api.auth import get_current_user
from app.utils.encryption import SecurityManager

router = APIRouter(prefix="/compliance", tags=["Compliance"])

@router.get("/summary", response_model=Dict[str, Any])
def get_compliance_summary(
    request: Request,
    framework_id: int = Query(None), # Optional Filter
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Returns compliance summary for the CURRENT TENANT (User's environment).
    """
    tenant_id = request.state.tenant_id
    return _get_summary_for_tenant(db, tenant_id, framework_id)

@router.get("/trust-center", response_model=Dict[str, Any])
def get_trust_center_summary(
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Returns compliance summary for the PLATFORM itself (System/Default Tenant).
    Visible to all authenticated users.
    """
    # Hardcoded to 'default_tenant' which holds the System's compliance data
    return _get_summary_for_tenant(db, "default_tenant")

def _get_summary_for_tenant(db: Session, tenant_id: str, framework_id: int = None):
    # 1. ENFORCE ENTITLEMENTS: Get Active Framework parameters
    # Resolve Tenant Internal ID from Slug (session tenant_id is slug)
    if tenant_id == "default_tenant":
        # System Admin sees everything (or we could enforce system settings too, but usually open)
        pass
    else:
        tenant_obj = db.query(Tenant).filter(Tenant.slug == tenant_id).first()
        if not tenant_obj:
            return {"summary": []} # Should filter or error
            
        # Get Active Framework IDs
        active_links = db.query(TenantFramework).filter(
            TenantFramework.tenant_id == tenant_obj.internal_tenant_id,
            TenantFramework.is_active == True
        ).all()
        active_fw_ids = [link.framework_id for link in active_links]
        
        # If no active frameworks, return empty immediately
        if not active_fw_ids:
            return {"summary": []}

    # Query: Get Scanned Results mapped to Control Domains
    query = db.query(ComplianceResult, Control.domain)\
        .join(Control, ComplianceResult.control_id == Control.control_id)\
        .filter(ComplianceResult.tenant_id == tenant_id)
        
    # Enforce Framework Entitlement
    if tenant_id != "default_tenant":
        query = query.filter(Control.framework_id.in_(active_fw_ids))
        
    if framework_id:
        # Additional user filter
        # Ensure requested framework is actually active
        if tenant_id != "default_tenant" and framework_id not in active_fw_ids:
             return {"summary": []}
             
        query = query.filter(Control.framework_id == framework_id)
        
    if framework_id:
        query = query.filter(Control.framework_id == framework_id)
        
    results = query.all()
    
    # Process Results
    domain_stats = {} 
    
    for result, domain in results:
        if not domain: domain = "Uncategorized"
        if domain not in domain_stats:
            domain_stats[domain] = {"total": 0, "pass": 0, "fail": 0}
            
        domain_stats[domain]["total"] += 1
        if result.status == "PASS":
            domain_stats[domain]["pass"] += 1
        elif result.status == "FAIL":
            domain_stats[domain]["fail"] += 1
            
    # Calculate Percentages
    summary = []
    for domain, stats in domain_stats.items():
        total = stats["total"]
        percentage = round((stats["pass"] / total) * 100, 1) if total > 0 else 0.0
        summary.append({
            "domain": domain,
            "stats": stats,
            "percentage": percentage,
            "status": "PASS" if percentage == 100 else "FAIL"
        })
        
    return {"summary": summary}

@router.get("/trust-center/domain/{domain}/details")
def get_trust_center_domain_details(
    domain: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Returns detailed system controls for Trust Center.
    Target: 'default_tenant'.
    """
    return _get_domain_details_for_tenant(db, "default_tenant", domain)

@router.get("/domain/{domain}/details")
def get_domain_details(
    domain: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Returns detailed control results for a specific domain for CURRENT TENANT.
    """
    tenant_id = request.state.tenant_id
    return _get_domain_details_for_tenant(db, tenant_id, domain)

def _get_domain_details_for_tenant(db: Session, tenant_id: str, domain: str):
    results = (
        db.query(ComplianceResult, Control.title, Control.description)
        .join(Control, ComplianceResult.control_id == Control.control_id)
        .filter(
            ComplianceResult.tenant_id == tenant_id,
            Control.domain == domain
        )
        .all()
    )
    
    details = []
    for res, title, desc in results:
        # Decrypt Metadata
        decrypted_evidence = {}
        if res.evidence_metadata:
            try:
                decrypted_evidence = SecurityManager.decrypt_metadata(res.evidence_metadata)
            except Exception as e:
                print(f"Decryption error for {res.control_id}: {e}")
                decrypted_evidence = {"error": "Failed to decrypt evidence"}
                
        details.append({
            "control_id": res.control_id,
            "title": title,
            "description": desc,
            "status": res.status,
            "last_scanned": res.last_scanned_at,
            "evidence": decrypted_evidence
        })
        
    return {"domain": domain, "controls": details}
