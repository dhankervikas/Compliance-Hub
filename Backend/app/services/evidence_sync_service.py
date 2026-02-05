from sqlalchemy.orm import Session
from app.models.evidence import Evidence
from app.models.control import Control
from app.models.universal_intent import UniversalIntent
from app.models.intent_framework_crosswalk import IntentFrameworkCrosswalk
from app.models.framework import Framework
import copy

def sync_evidence_by_intent(db: Session, evidence_id: int, master_intent_id: str):
    """
    Antigravity Directive 3: Evidence Gravity
    Finds all controls linked to the given intent_id and propagates the evidence to them.
    """
    print(f"[Evidence Gravity] Syncing Evidence {evidence_id} for Intent '{master_intent_id}'...")
    
    # 1. Get Source Evidence
    source_evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not source_evidence:
        print(f"[Evidence Gravity] Evidence {evidence_id} not found.")
        return

    # 2. Get/Validate Universal Intent
    intent = db.query(UniversalIntent).filter(UniversalIntent.intent_id == master_intent_id).first()
    if not intent:
        print(f"[Evidence Gravity] UniversalIntent '{master_intent_id}' not found. Creating placeholder...")
        # Auto-create intent to allow system to learn
        intent = UniversalIntent(
            intent_id=master_intent_id,
            description=f"Auto-generated intent for {master_intent_id}",
            category="General"
        )
        db.add(intent)
        db.flush() 

    # 3. Find Crosswalk Mappings
    # (In a real scenario, this relies on seeded Crosswalk data. 
    # For now, we look for CROSSWALKS that match this intent.)
    
    # OPTIMIZATION: If no crosswalks exist yet, we can't sync.
    # But we can try to find controls that *should* be mapped if we had logic.
    # For this implementation, we rely on `IntentFrameworkCrosswalk`.
    
    mappings = db.query(IntentFrameworkCrosswalk).filter(IntentFrameworkCrosswalk.intent_id == intent.id).all()
    
    targets_orphaned = 0
    targets_synced = 0
    
    found_controls = []
    
    # Resolve Mappings to Controls
    for mapping in mappings:
        # Find Framework ID
        fw = db.query(Framework).filter(Framework.code == mapping.framework_id).first()
        if not fw:
            continue
            
        # Find Control
        target_ctrl = db.query(Control).filter(
            Control.control_id == mapping.control_reference,
            Control.framework_id == fw.id
        ).first()
        
        if target_ctrl:
            found_controls.append(target_ctrl)
    
    # 4. Propagate Evidence (Clone)
    for ctrl in found_controls:
        if ctrl.id == source_evidence.control_id:
            continue # Skip self validation
            
        # Check if already exists linked to this control (avoid dupes)
        existing = db.query(Evidence).filter(
            Evidence.control_id == ctrl.id,
            Evidence.filename == source_evidence.filename,
            Evidence.master_intent_id == master_intent_id
        ).first()
        
        if existing:
            print(f" -> Skipping {ctrl.control_id} (Evidence already exists)")
            continue
            
        # CLONE
        new_evidence = Evidence(
            filename=source_evidence.filename,
            file_path=source_evidence.file_path,
            file_size=source_evidence.file_size,
            file_type=source_evidence.file_type,
            tenant_id=source_evidence.tenant_id,
            title=source_evidence.title,
            description=source_evidence.description,
            control_id=ctrl.id,
            uploaded_by=source_evidence.uploaded_by,
            collection_date=source_evidence.collection_date,
            tags=source_evidence.tags,
            status=source_evidence.status,
            validation_source="automated_gravity",
            master_intent_id=master_intent_id
        )
        db.add(new_evidence)
        targets_synced += 1
        print(f" -> Synced to {ctrl.control_id} ({ctrl.framework.code})")

    db.commit()
    print(f"[Evidence Gravity] Sync Complete. Propagated to {targets_synced} controls.")

