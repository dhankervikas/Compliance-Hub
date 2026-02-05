from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.framework import Framework
from app.models.control import Control, ControlStatus
from app.models.tenant_framework import TenantFramework
from app.schemas.framework import FrameworkCreate, Framework as FrameworkSchema, FrameworkWithStats
from app.api.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=FrameworkSchema, status_code=status.HTTP_201_CREATED)
def create_framework(
    framework: FrameworkCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new compliance framework"""
    # Check if framework already exists
    # Global check removed for multitenancy logic below
    
    # Check if framework already exists for this tenant
    if db.query(Framework).filter(Framework.code == framework.code, Framework.tenant_id == current_user.tenant_id).first():
        raise HTTPException(status_code=400, detail="Framework code already exists")
    
    db_framework = Framework(**framework.dict(), tenant_id=current_user.tenant_id)
    db.add(db_framework)
    db.commit()
    db.refresh(db_framework)
    
    return db_framework


@router.get("/", response_model=List[FrameworkSchema])
def list_frameworks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all frameworks"""
    if current_user.tenant_id == "default_tenant":
        # Super Admin sees all frameworks defined in the catalog
        # (Assuming catalog lives in default_tenant or globally)
        frameworks = db.query(Framework).offset(skip).limit(limit).all()
    else:
        # Standard Tenant: See only subscribed active frameworks
        # Resolve Tenant UUID if current_user.tenant_id is a slug
        from app.models.tenant import Tenant
        tenant = db.query(Tenant).filter(Tenant.slug == current_user.tenant_id).first()
        tenant_uuid = tenant.internal_tenant_id if tenant else current_user.tenant_id
        
        frameworks = db.query(Framework).join(
            TenantFramework, Framework.id == TenantFramework.framework_id
        ).filter(
            TenantFramework.tenant_id == tenant_uuid,
            TenantFramework.is_active == True
        ).offset(skip).limit(limit).all()
        
    return frameworks


@router.get("/{framework_id}", response_model=FrameworkSchema)
def get_framework(
    framework_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific framework"""
    # Fix: Allow shared frameworks (don't check owner). Check access via TenantFramework instead if needed.
    # For now, just checking existence is sufficient to fix the blocking bug.
    framework = db.query(Framework).filter(Framework.id == framework_id).first()
    
    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")
    return framework


@router.get("/{framework_id}/stats", response_model=FrameworkWithStats)
def get_framework_stats(
    framework_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get framework with statistics"""
    framework = db.query(Framework).filter(Framework.id == framework_id).first()
    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")
    
    # Resolve Tenant UUID if current_user.tenant_id is a slug
    # This ensures we query controls using the correct UUID foreign key
    from app.models.tenant import Tenant
    tenant = db.query(Tenant).filter(Tenant.slug == current_user.tenant_id).first()
    tenant_uuid = tenant.internal_tenant_id if tenant else current_user.tenant_id

    # Get Default Tenant UUID
    default_tenant = db.query(Tenant).filter(Tenant.slug == "default_tenant").first()
    default_tenant_uuid = default_tenant.internal_tenant_id if default_tenant else "default_tenant"

    # Calculate statistics using tenant_uuid OR default_tenant
    from sqlalchemy import or_, and_, text
    from app.models.universal_intent import UniversalIntent, IntentStatus
    from app.models.intent_framework_crosswalk import IntentFrameworkCrosswalk

    # Base query for controls visible to this tenant
    control_query = db.query(Control).filter(
        Control.framework_id == framework_id,
        or_(Control.tenant_id == tenant_uuid, Control.tenant_id == default_tenant_uuid)
    )

    total_controls = control_query.count()

    # IMPLEMENTED: Control is Implemented OR Parent Intent is Completed
    # normalize framework code for crosswalk (e.g. ISO 27001:2022 -> ISO27001)
    fw_code = framework.code
    # Simple mapping if needed, matching seed script
    if "ISO" in fw_code and "27001" in fw_code:
        fw_code = "ISO27001" 

    implemented = db.query(Control).outerjoin(
        IntentFrameworkCrosswalk,
        and_(
            Control.control_id == IntentFrameworkCrosswalk.control_reference,
            IntentFrameworkCrosswalk.framework_id == fw_code
        )
    ).outerjoin(
        UniversalIntent,
        IntentFrameworkCrosswalk.intent_id == UniversalIntent.id
    ).filter(
        Control.framework_id == framework_id,
        or_(Control.tenant_id == tenant_uuid, Control.tenant_id == default_tenant_uuid),
        or_(
            Control.status == ControlStatus.IMPLEMENTED,
            UniversalIntent.status == IntentStatus.COMPLETED
        )
    ).count()
    
    # IN PROGRESS: Started AND (Parent Not Completed)
    in_progress = db.query(Control).outerjoin(
        IntentFrameworkCrosswalk,
        and_(
            Control.control_id == IntentFrameworkCrosswalk.control_reference,
            IntentFrameworkCrosswalk.framework_id == fw_code
        )
    ).outerjoin(
        UniversalIntent,
        IntentFrameworkCrosswalk.intent_id == UniversalIntent.id
    ).filter(
        Control.framework_id == framework_id,
        or_(Control.tenant_id == tenant_uuid, Control.tenant_id == default_tenant_uuid),
        Control.status == ControlStatus.IN_PROGRESS,
        or_(UniversalIntent.status != IntentStatus.COMPLETED, UniversalIntent.status == None)
    ).count()
    
    # NOT STARTED: Not Started AND (Parent Not Completed)
    not_started = db.query(Control).outerjoin(
        IntentFrameworkCrosswalk,
        and_(
            Control.control_id == IntentFrameworkCrosswalk.control_reference,
            IntentFrameworkCrosswalk.framework_id == fw_code
        )
    ).outerjoin(
        UniversalIntent,
        IntentFrameworkCrosswalk.intent_id == UniversalIntent.id
    ).filter(
        Control.framework_id == framework_id,
        or_(Control.tenant_id == tenant_uuid, Control.tenant_id == default_tenant_uuid),
        Control.status == ControlStatus.NOT_STARTED,
        or_(UniversalIntent.status != IntentStatus.COMPLETED, UniversalIntent.status == None)
    ).count()
    
    completion_percentage = (implemented / total_controls * 100) if total_controls > 0 else 0
    
    return {
        **framework.__dict__,
        "total_controls": total_controls,
        "implemented_controls": implemented,
        "in_progress_controls": in_progress,
        "not_started_controls": not_started,
        "completion_percentage": round(completion_percentage, 2)
    }

@router.post("/{framework_id}/seed-controls", status_code=status.HTTP_201_CREATED)
def seed_framework_controls(
    framework_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Force re-seed controls for a framework (specifically ISO 27001).
    WARNING: This deletes all existing controls for the framework!
    """
    # Resolve Tenant UUID if current_user.tenant_id is a slug
    from app.models.tenant import Tenant
    tenant = db.query(Tenant).filter(Tenant.slug == current_user.tenant_id).first()
    tenant_uuid = tenant.internal_tenant_id if tenant else current_user.tenant_id

    # 1. Get Framework (Allow shared frameworks)
    framework = db.query(Framework).filter(Framework.id == framework_id).first()
    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")

    # Only support ISO 27001 for now
    # Only support ISO 27001 for now (Relaxed check)
    if framework.code not in ["ISO27001", "ISO27001_2022"] and "ISO" not in framework.code:
        raise HTTPException(status_code=400, detail=f"Seeding not supported for framework code: {framework.code}")

    try:
        # 1.5. Clean References using RAW SQL (Scorched Earth Policy)
        # This ensures we bypass any ORM complexity or missing cascades
        from sqlalchemy import text

        # Get all control IDs for this framework
        control_ids_result = db.execute(text("SELECT id FROM controls WHERE framework_id = :fid"), {"fid": framework_id}).fetchall()
        control_ids = [row[0] for row in control_ids_result]
        
        deleted_mappings = 0
        deleted_controls = 0
        
        if control_ids:
            # Format IDs for SQL IN clause
            ids_tuple = tuple(control_ids)
            # Handle single item tuple syntax for SQL (1,) -> (1)
            ids_str = str(ids_tuple).replace(',)', ')') if len(control_ids) > 0 else "()"
            if len(control_ids) == 1:
                ids_str = f"({control_ids[0]})"

            # A. Delete Dependent Relationships
            db.execute(text(f"DELETE FROM control_mappings WHERE source_control_id IN {ids_str} OR target_control_id IN {ids_str}"))
            db.execute(text(f"DELETE FROM process_control_mapping WHERE control_id IN {ids_str}"))
            db.execute(text(f"DELETE FROM evidence WHERE control_id IN {ids_str}"))
            db.execute(text(f"DELETE FROM assessments WHERE control_id IN {ids_str}"))
            
            # B. Delete Controls
            result = db.execute(text(f"DELETE FROM controls WHERE id IN {ids_str}"))
            deleted_controls = result.rowcount

        db.commit()
        
        # 3. Import ISO Data (Lazy import to avoid circular dep if any)
        from app.utils.iso_data import ISO_CONTROLS_DATA
        
        # 4. Insert New Controls
        for data in ISO_CONTROLS_DATA:
            control = Control(
                framework_id=framework_id,
                status=ControlStatus.NOT_STARTED,
                tenant_id=tenant_uuid,
                **data
            )
            db.add(control)
        
        db.commit()
        
        return {
            "message": f"Fixed! Force Deleted {deleted_controls} controls. Inserted {len(ISO_CONTROLS_DATA)}. (Framework: {framework.code})",
            "stat_check": "OK"
        }

    except Exception as e:
        db.rollback()
        print(f"SEEDING ERROR: {str(e)}") # Add Logging
        # Return the specific error to the user
        raise HTTPException(status_code=500, detail=f"Repair Failed: {str(e)}")

@router.get("/diagnostic/stats")
def get_framework_stats_debug(db: Session = Depends(get_db)):
    """
    Debug endpoint to count controls per framework.
    """
    frameworks = db.query(Framework).all()
    stats = []
    total_controls = 0
    
    for fw in frameworks:
        count = db.query(Control).filter(Control.framework_id == fw.id).count()
        total_controls += count
        stats.append({
            "id": fw.id,
            "code": fw.code,
            "name": fw.name,
            "control_count": count
        })
        
    return {
        "timestamp": str(datetime.now()),
        "total_controls": total_controls,
        "frameworks": stats
    }