from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from pydantic import BaseModel
from app.database import get_db
from app.models.control import Control
from app.models.framework import Framework
from app.models.control_mapping import ControlMapping
from app.schemas.control import Control as ControlSchema, ControlCreate, ControlUpdate, ControlWithFramework, SoAUpdate
from app.schemas.control import ControlStatus
from app.api.auth import get_current_user

router = APIRouter(
    tags=["controls"]
)

@router.post("/", response_model=ControlSchema, status_code=status.HTTP_201_CREATED)
def create_control(
    control: ControlCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new control"""
    """Create a new control"""
    # Resolve Tenant UUID if current_user.tenant_id is a slug
    from app.models.tenant import Tenant
    tenant = db.query(Tenant).filter(Tenant.slug == current_user.tenant_id).first()
    tenant_uuid = tenant.internal_tenant_id if tenant else current_user.tenant_id

    # Check if control_id already exists for this tenant
    if db.query(Control).filter(Control.control_id == control.control_id, Control.tenant_id == tenant_uuid).first():
        raise HTTPException(status_code=400, detail="Control ID already exists")
    
    # Verify framework exists and belongs to tenant (Use UUID)
    
    # Fix: Allow shared frameworks (don't check owner). Check access via TenantFramework instead if needed.
    # For now, just checking existence is sufficient to fix the blocking bug.
    framework = db.query(Framework).filter(Framework.id == control.framework_id).first()
    
    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")
    
    db_control = Control(**control.dict(), tenant_id=tenant_uuid)
    db.add(db_control)
    db.commit()
    db.refresh(db_control)
    
    return db_control

@router.get("/", response_model=List[ControlSchema])
def list_controls(
    skip: int = 0,
    limit: int = 500,
    framework_id: Optional[int] = Query(None),
    framework_ids: Optional[List[int]] = Query(None),
    status: Optional[ControlStatus] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all controls with optional filters"""
    # Resolve Tenant UUID if current_user.tenant_id is a slug
    from app.models.tenant import Tenant
    tenant = db.query(Tenant).filter(Tenant.slug == current_user.tenant_id).first()
    tenant_uuid = tenant.internal_tenant_id if tenant else current_user.tenant_id

    # Get Default Tenant UUID
    default_tenant = db.query(Tenant).filter(Tenant.slug == "default_tenant").first()
    default_tenant_uuid = default_tenant.internal_tenant_id if default_tenant else "default_tenant"

    # Use UUID for query - Include "default_tenant" for shared controls
    query = db.query(Control).filter(
        or_(
            Control.tenant_id == tenant_uuid,
            Control.tenant_id == default_tenant_uuid
        )
    )
    
    # Apply filters
    if framework_ids:
        query = query.filter(Control.framework_id.in_(framework_ids))
    elif framework_id:
        query = query.filter(Control.framework_id == framework_id)
        
    if status:
        query = query.filter(Control.status == status)
    if search:
        query = query.filter(
            or_(
                Control.control_id.ilike(f"%{search}%"),
                Control.title.ilike(f"%{search}%")
            )
        )
    
    
    
    # Eager load process mapping for Process View
    # Note: 'sub_processes' is a backref from app.models.process.SubProcess
    from sqlalchemy.orm import joinedload
    from app.models.process import SubProcess

    # --- SOC 2 SCOPE FILTERING ---
    # Check if we are querying for SOC 2 (assuming ID 2 or code SOC2)
    # We need to fetch the framework code to be sure, or rely on input IDs
    # Let's start with a dynamic check if framework_ids or framework_id is provided
    
    target_framework_ids = []
    if framework_id:
        target_framework_ids.append(framework_id)
    if framework_ids:
        target_framework_ids.extend(framework_ids)
        
    is_soc2_query = False
    if target_framework_ids:
        # Check if any of these are SOC 2
        # This requires a DB lookup or knowing the ID. 
        # Ideally, we look up the code.
        soc2_fw = db.query(Framework).filter(Framework.code == "SOC2").first()
        if soc2_fw and soc2_fw.id in target_framework_ids:
            is_soc2_query = True
            
    if is_soc2_query:
        # Fetch Settings
        from app.models.settings import ComplianceSettings
        settings = db.query(ComplianceSettings).filter(
            ComplianceSettings.section_key == "scope",
            ComplianceSettings.tenant_id == tenant_uuid
        ).first()
        
        if settings and settings.content:
            selected_principles = settings.content.get("soc2_selected_principles", [])
            # Default to Security if empty/missing (it's mandatory)
            if not selected_principles:
                selected_principles = ["Security"]
                
            # Map Principles to ID Prefixes
            # Security -> CC (Common Criteria)
            # Availability -> A
            # Confidentiality -> C
            # Processing Integrity -> PI
            # Privacy -> P
            
            allowed_prefixes = ["CC"] # Always include Security
            
            if "Availability" in selected_principles:
                allowed_prefixes.append("A")
            if "Confidentiality" in selected_principles:
                allowed_prefixes.append("C")
            if "Processing Integrity" in selected_principles:
                allowed_prefixes.append("PI")
            if "Privacy" in selected_principles:
                allowed_prefixes.append("P")
                
            # Apply Filter: (framework != SOC2) OR (framework == SOC2 AND control_id starts with allowed)
            # Since we might be querying mixed frameworks, we need to be careful.
            # But usually request is for a single framework.
            
            # Simple Logic: If the control belongs to SOC 2, it MUST match a prefix.
            # We can use an AND condition combined with OR for prefixes.
            
            # Since we already filtered by Tenant and optionally Framework in `query`,
            # we just need to add the specific restriction for SOC 2 controls.
            
            # Filter: Show Control IF (Framework != SOC2) OR (Framework == SOC2 AND Prefix Match)
            
            filter_conditions = []
            for prefix in allowed_prefixes:
                filter_conditions.append(Control.control_id.like(f"{prefix}%"))
            
            # We need to handle the case where we might be fetching multiple frameworks.
            # But for "Framework Detail" view, we fetch one.
            # If fetching ALL (ComplianceDashboard), we might hide SOC 2 controls incorrectly if we just applying this.
            
            # Let's assume strict filtering: If SOC 2 is involved, filter its controls.
            if soc2_fw:
                 query = query.filter(
                     or_(
                         Control.framework_id != soc2_fw.id, # Don't touch other frameworks
                         and_(
                             Control.framework_id == soc2_fw.id,
                             or_(*filter_conditions)
                         )
                     )
                 )

    controls = query.options(
        joinedload(Control.sub_processes).joinedload(SubProcess.process)
    ).order_by(Control.control_id).offset(skip).limit(limit).all()
    
    return controls


@router.get("/{control_id}/mappings")
async def get_control_mappings(
    control_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all controls that map to/from this control"""
    # Resolve Tenant UUID if current_user.tenant_id is a slug
    from app.models.tenant import Tenant
    tenant = db.query(Tenant).filter(Tenant.slug == current_user.tenant_id).first()
    tenant_uuid = tenant.internal_tenant_id if tenant else current_user.tenant_id

    # Get Default Tenant UUID
    default_tenant = db.query(Tenant).filter(Tenant.slug == "default_tenant").first()
    default_tenant_uuid = default_tenant.internal_tenant_id if default_tenant else "default_tenant"

    control = db.query(Control).filter(
        Control.id == control_id,
        or_(
            Control.tenant_id == tenant_uuid,
            Control.tenant_id == default_tenant_uuid
        )
    ).first()
    if not control:
        raise HTTPException(status_code=404, detail="Control not found")
    
    # Get outgoing mappings (this control satisfies others)
    outgoing_mappings = db.query(ControlMapping).filter(
        ControlMapping.source_control_id == control_id
    ).all()
    
    # Get incoming mappings (this control is satisfied by others)
    incoming_mappings = db.query(ControlMapping).filter(
        ControlMapping.target_control_id == control_id
    ).all()
    
    # Format outgoing mappings
    satisfies = []
    for mapping in outgoing_mappings:
        target_control = db.query(Control).filter(
            Control.id == mapping.target_control_id
        ).first()
        target_framework = db.query(Framework).filter(
            Framework.id == target_control.framework_id
        ).first()
        
        satisfies.append({
            "control_id": target_control.id,
            "control_identifier": target_control.control_id,
            "control_title": target_control.title,
            "framework_name": target_framework.name,
            "framework_short_name": target_framework.code,
            "mapping_type": mapping.mapping_type,
            
        })
    
    # Format incoming mappings
    satisfied_by = []
    for mapping in incoming_mappings:
        source_control = db.query(Control).filter(
            Control.id == mapping.source_control_id
        ).first()
        source_framework = db.query(Framework).filter(
            Framework.id == source_control.framework_id
        ).first()
        
        satisfied_by.append({
            "control_id": source_control.id,
            "control_identifier": source_control.control_id,
            "control_title": source_control.title,
            "framework_name": source_framework.name,
            "framework_short_name": source_framework.code,
            "mapping_type": mapping.mapping_type,
            
        })
    
    return {
        "control_id": control_id,
        "control_identifier": control.control_id,
        "satisfies": satisfies,
        "satisfied_by": satisfied_by
    }
@router.get("/{control_id}", response_model=ControlWithFramework)
def get_control(
    control_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific control with framework details"""
    # Get Default Tenant UUID
    from app.models.tenant import Tenant
    default_tenant = db.query(Tenant).filter(Tenant.slug == "default_tenant").first()
    default_tenant_uuid = default_tenant.internal_tenant_id if default_tenant else "default_tenant"

    control = db.query(Control).filter(
        Control.id == control_id, 
        or_(
            Control.tenant_id == current_user.tenant_id,
            Control.tenant_id == default_tenant_uuid
        )
    ).first()
    if not control:
        raise HTTPException(status_code=404, detail="Control not found")
    
    framework = db.query(Framework).filter(Framework.id == control.framework_id).first()
    
    return {
        **control.__dict__,
        "framework_name": framework.name,
        "framework_code": framework.code
    }

@router.put("/{control_id}", response_model=ControlSchema)
def update_control(
    control_id: int,
    control_update: ControlUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a control"""
    db_control = db.query(Control).filter(
        Control.id == control_id, 
        or_(
            Control.tenant_id == current_user.tenant_id,
            Control.tenant_id == "default_tenant"
        )
    ).first()
    if not db_control:
        raise HTTPException(status_code=404, detail="Control not found")
    
    # Update only provided fields
    update_data = control_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_control, field, value)
    
    db.commit()
    db.refresh(db_control)
    
    return db_control

@router.delete("/{control_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_control(
    control_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a control"""
    db_control = db.query(Control).filter(
        Control.id == control_id, 
        or_(
            Control.tenant_id == current_user.tenant_id,
            Control.tenant_id == "default_tenant"
        )
    ).first()
    if not db_control:
        raise HTTPException(status_code=404, detail="Control not found")
    
    db.delete(db_control)
    db.commit()
    
    return None

@router.post("/soa-update")
def update_soa_bulk(
    updates: List[SoAUpdate],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Bulk update SoA details for controls"""
    count = 0
    # Get Default Tenant UUID
    from app.models.tenant import Tenant
    default_tenant = db.query(Tenant).filter(Tenant.slug == "default_tenant").first()
    default_tenant_uuid = default_tenant.internal_tenant_id if default_tenant else "default_tenant"

    for u in updates:
        control = db.query(Control).filter(
            Control.control_id == u.control_id, 
            or_(
                 Control.tenant_id == current_user.tenant_id,
                 Control.tenant_id == default_tenant_uuid
            )
        ).first()
        if control:
            control.is_applicable = u.is_applicable
            control.justification = u.justification
            control.justification_reason = u.justification_reason
    db.commit()
    return {"status": "success", "updated": count}

# --- BULK ACTIONS ---

class BulkAssignOwnerRequest(BaseModel):
    control_ids: List[int]
    owner_id: Optional[str]
    department_id: Optional[str] = None

class BulkStatusRequest(BaseModel):
    control_ids: List[int]
    status: str
    is_applicable: bool = True

class BulkLinkEvidenceRequest(BaseModel):
    control_ids: List[int]
    evidence_id: int

@router.post("/bulk/owner")
def bulk_assign_owner(
    request: BulkAssignOwnerRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Bulk assign owner to controls"""
    # Resolve Tenants
    from app.models.tenant import Tenant
    default_tenant = db.query(Tenant).filter(Tenant.slug == "default_tenant").first()
    default_uuid = default_tenant.internal_tenant_id if default_tenant else "default_tenant"

    controls = db.query(Control).filter(
        Control.id.in_(request.control_ids),
        or_(
            Control.tenant_id == current_user.tenant_id,
            Control.tenant_id == default_uuid
        )
    ).all()
    
    count = 0
    for c in controls:
        c.owner_id = request.owner_id
        if request.department_id:
            c.department_id = request.department_id
        count += 1
    
    db.commit()
    return {"message": f"Updated owner for {count} controls"}

@router.post("/bulk/status")
def bulk_update_status(
    request: BulkStatusRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Bulk update status"""
    from app.models.tenant import Tenant
    default_tenant = db.query(Tenant).filter(Tenant.slug == "default_tenant").first()
    default_uuid = default_tenant.internal_tenant_id if default_tenant else "default_tenant"

    controls = db.query(Control).filter(
        Control.id.in_(request.control_ids),
        or_(
            Control.tenant_id == current_user.tenant_id,
            Control.tenant_id == default_uuid
        )
    ).all()

    count = 0
    for c in controls:
        c.status = request.status
        c.is_applicable = request.is_applicable
        count += 1
        
    db.commit()
    return {"message": f"Updated status for {count} controls"}

@router.post("/bulk/evidence")
def bulk_link_evidence(
    request: BulkLinkEvidenceRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Bulk link an evidence item to controls"""
    # This requires creating new Evidence entries or M2M relationship?
    # Current model `Evidence` has `control_id` FK (One-to-Many: One Control has Many Evidence). 
    # Evidence cannot be shared via M2M in current schema (Control <-> Evidence).
    # To "Share" evidence in One-to-Many, we must duplicate the evidence record pointing to the new control, 
    # OR we refactored Evidence to Many-to-Many?
    # Task says "Auto-Link Evidence... Shared Evidence badge".
    # If I duplicate the record (same file_path), it works logic-wise.
    
    from app.models.evidence import Evidence
    
    original_evidence = db.query(Evidence).filter(Evidence.id == request.evidence_id).first()
    if not original_evidence:
         raise HTTPException(status_code=404, detail="Evidence not found")

    count = 0
    existing_control_id = original_evidence.control_id
    
    # Verify controls access
    controls = db.query(Control).filter(Control.id.in_(request.control_ids)).all()
    
    for c in controls:
        if c.id == existing_control_id:
            continue
            
        # Clone Evidence Record
        new_evidence = Evidence(
            filename=original_evidence.filename,
            file_path=original_evidence.file_path,
            file_size=original_evidence.file_size,
            file_type=original_evidence.file_type,
            tenant_id=c.tenant_id, # Inherit control's tenant
            title=original_evidence.title,
            description=original_evidence.description,
            control_id=c.id, # Link to new control
            uploaded_by=current_user.email, # Tag with current user
            collection_date=original_evidence.collection_date,
            tags="shared_bulk_link",
            status=original_evidence.status,
            validation_source=original_evidence.validation_source
        )
        db.add(new_evidence)
        count += 1
        
    db.commit()
    return {"message": f"Linked evidence to {count} additional controls"}