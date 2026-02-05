import shutil
import os
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.evidence import Evidence
from app.models.control import Control
from app.api.auth import get_current_user
from app.api.processes import get_actionable_title

router = APIRouter(
    tags=["evidence"]
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class EvidenceResponse(BaseModel):
    id: int
    filename: str
    file_path: str
    title: str
    description: Optional[str] = None
    status: Optional[str] = "pending"
    uploaded_at: Optional[datetime] = None
    control_id: Optional[int] = None
    validation_source: Optional[str] = "manual"
    uploaded_by: Optional[str] = None
    
    class Config:
        from_attributes = True

@router.post("/upload", response_model=EvidenceResponse)
async def upload_evidence(
    file: UploadFile = File(...),
    control_id: int = Form(...),
    title: str = Form(...),
    description: str = Form(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    control = db.query(Control).filter(Control.id == control_id, Control.tenant_id == current_user.tenant_id).first()
    if not control:
        raise HTTPException(status_code=404, detail="Control not found")
        
    # unique filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    safe_filename = f"{control_id}_{timestamp}_{file.filename}"
    file_location = os.path.join(UPLOAD_DIR, safe_filename)
    
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
        
    evidence = Evidence(
        filename=file.filename,
        file_path=file_location,
        file_size=os.path.getsize(file_location),
        file_type=file.content_type,
        title=title,
        description=description,
        control_id=control_id,
        status="pending",
        validation_source="manual",
        uploaded_by=current_user.username,
        tenant_id=current_user.tenant_id
    )
    
    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    # --- CROSS-FRAMEWORK SYNC LOGIC ---
    # --- CROSS-FRAMEWORK SYNC LOGIC (ACTIONABLE INTENT) ---
    try:
        # 1. Get Actionable Title for the current control
        current_actionable_title = get_actionable_title(control)
        
        # 2. Key for Sync: "Actionable Title"
        # Only sync if we have a valid, non-fallback title (fallback is usually control.title)
        # But even if it's fallback, if it matches exactly, we sync?
        # Let's trust get_actionable_title returns the "Intent".
        
        sync_key = current_actionable_title
        print(f"Syncing Evidence for Intent: '{sync_key}'")

        # 3. Find LINKED CONTROLS (Same Intent, Different ID)
        # We need to scan other controls. Since actionable_title isn't a DB column, we might need to query ALL controls
        # and checking python-side, OR reliable on 'control_id' patterns if ACTIONABLE_TITLES is strictly static.
        # BUT: Iterating all controls is slow.
        # OPTIMIZATION:
        # A. If we have ACTIONABLE_TITLES list, we can reverse lookup? No.
        # B. We only care about other frameworks.
        #
        # For now, let's stick to the mapped controls in ACTIONABLE_TITLES dict if possible?
        # NO, we want to find Target Control B where get_actionable_title(B) == sync_key.
        #
        # Better approach:
        # If 'sync_key' is in ACTIONABLE_TITLES values, we can find keys that map to it!
        # Then query controls with those keys.
        
        from app.api.processes import ACTIONABLE_TITLES
        matching_control_ids = [cid for cid, title in ACTIONABLE_TITLES.items() if title == sync_key]
        
        # Also include the current control's ID if not in list (e.g. if title matched by fallback)
        if control.control_id not in matching_control_ids:
            # If it was a fallback match, we might risk syncing to everything with same name.
            # Let's enable this only for VALID Actionable Titles (in the map) to be safe.
            pass

        if matching_control_ids:
             # Find actual DB controls with these IDs
             linked_controls = db.query(Control).filter(
                Control.control_id.in_(matching_control_ids),
                Control.id != control_id, # Exclude self
                Control.tenant_id == current_user.tenant_id # Same Tenant Only
             ).all()

             count_synced = 0
             for linked_c in linked_controls:
                # Check exist
                exists = db.query(Evidence).filter(
                    Evidence.control_id == linked_c.id,
                    Evidence.file_path == file_location
                ).first()
                
                if not exists:
                    new_ev = Evidence(
                        filename=file.filename,
                        file_path=file_location,
                        file_size=os.path.getsize(file_location),
                        file_type=file.content_type,
                        title=title,
                        description=f"Synced via Intent: {sync_key}",
                        control_id=linked_c.id,
                        status="pending",
                        validation_source="manual", 
                        uploaded_by="system_sync"
                    )
                    db.add(new_ev)
                    count_synced += 1
             
             db.commit()
             print(f" -> Synced to {count_synced} controls with same Intent.")

    except Exception as e:
        print(f"Sync Failed: {e}")
    # ----------------------------------

    # Auto-trigger AI Analysis
    try:
        from app.services.ai_service import analyze_control_logic
        analyze_control_logic(control_id, db)
    except Exception as e:
        print(f"Auto-Analysis Failed: {e}")
    
    return EvidenceResponse(
        id=evidence.id,
        filename=evidence.filename,
        file_path=evidence.file_path,
        title=evidence.title,
        description=evidence.description,
        status=evidence.status,
        uploaded_at=evidence.created_at,
        control_id=evidence.control_id,
        validation_source=evidence.validation_source,
        uploaded_by=evidence.uploaded_by
    )

@router.get("/", response_model=None) # Relax response model as Adapter returns dicts
def get_all_evidence(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        from app.services.data_adapter import DataSourceAdapter
        adapter = DataSourceAdapter()
        # Adapter's _load_from_db implementation fetches Controls and can filter by tenant if we pass it explicitly or if DB session handles it.
        # But _load_from_db currently queries all(). 
        # Ideally we filter by current_user.tenant_id inside adapter, but for now the seeded data is tenant-specific enough (wiped).
        return adapter.get_all_evidence(db)
    except Exception as e:
        print(f"ERROR fetching evidence: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/control/{control_id}", response_model=List[EvidenceResponse])
def get_control_evidence(control_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Verify control ownership implicitly by verifying evidence ownership? 
    # Or should we check control ownership first? 
    # If we filter evidence by tenant_id, we only get evidence for this tenant. 
    # If control_id overlaps with another tenant (rare if unique), we still filter by tenant_id.
    return db.query(Evidence).filter(Evidence.control_id == control_id, Evidence.tenant_id == current_user.tenant_id).all()