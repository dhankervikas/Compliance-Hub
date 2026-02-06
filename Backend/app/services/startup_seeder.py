from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.framework import Framework
from app.models.control import Control
from app.models.control_mapping import ControlMapping

# Import existing logic if possible, or re-implement simplistic checks
# We will duplicate the critical "Ensure Framework Exists" logic here for robustness

def seed_frameork_if_missing(db: Session, code: str, name: str, description: str, version: str):
    existing = db.query(Framework).filter(Framework.code == code).first()
    if not existing:
        print(f"[STARTUP SEED] Creating Framework: {name}")
        fw = Framework(
            name=name,
            code=code,
            description=description,
            version=version
        )
        db.add(fw)
        db.commit()
        db.refresh(fw)
        return fw
    return existing

def seed_sample_controls(db: Session, fw_id: int, controls_list: list):
    count = 0
    for c_text in controls_list:
        # Simple ID generation
        c_id = c_text[:12].upper().replace(" ", "-").replace(":", "").replace(".", "-")
        
        exists = db.query(Control).filter(Control.framework_id == fw_id, Control.control_id == c_id).first()
        if not exists:
            # Check if title is split by ":"
            parts = c_text.split(":", 1)
            if len(parts) > 1:
                 # "AC-1: Title"
                 # c_id could be AC-1
                 potential_id = parts[0].strip()
                 potential_title = parts[1].strip()
                 # Only use short ID if it looks like a code (no spaces, short)
                 if " " not in potential_id and len(potential_id) < 10:
                     c_id = potential_id
                     title = potential_title
                 else:
                     title = c_text
            else:
                title = c_text

            ctrl = Control(
                control_id=c_id,
                title=title,
                description=f"Standard requirement for {title}",
                framework_id=fw_id,
                category="General",
                priority="high",
                status="not_started"
            )
            db.add(ctrl)
            count += 1
    if count > 0:
        db.commit()
        print(f"[STARTUP SEED] Added {count} sample controls for Framework ID {fw_id}")

def run_startup_seed():
    """
    Called by main.py on startup. 
    Orchestrates the population of ALL frameworks.
    """
    db = SessionLocal()
    try:
        # 1. DEFINE ALL FRAMEWORKS TO SEED
        FRAMEWORKS_TO_SEED = [
            {"code": "SOC2", "name": "SOC 2 Type II", "desc": "AICPA Trust Services Criteria", "version": "2017"},
            {"code": "ISO27001", "name": "ISO 27001:2022", "desc": "Information Security Management", "version": "2022"},
            {"code": "NIST_CSF_2.0", "name": "NIST CSF 2.0", "desc": "Cybersecurity Framework", "version": "2.0"},
            {"code": "HIPAA", "name": "HIPAA Security Rule", "desc": "Protection of electronic protected health information (ePHI).", "version": "1.0"},
            {"code": "PCI_DSS_v4", "name": "PCI DSS v4.0", "desc": "Payment Card Industry Data Security Standard.", "version": "4.0"},
            {"code": "ISO_27701", "name": "ISO/IEC 27701:2019", "desc": "Privacy Information Management System (PIMS).", "version": "2019"},
            {"code": "ISO_42001", "name": "ISO/IEC 42001:2023", "desc": "Artificial Intelligence Management System (AIMS).", "version": "2023"},
            {"code": "GDPR", "name": "GDPR", "desc": "General Data Protection Regulation.", "version": "2016"}
        ]

        print("[STARTUP SEED] Verifying Frameworks exist...")
        for fw_def in FRAMEWORKS_TO_SEED:
            fw = seed_frameork_if_missing(db, fw_def["code"], fw_def["name"], fw_def["desc"], fw_def["version"])
            
            # OPTIONAL: Add a dummy control if empty so it looks 'active' in dashboard
            count = db.query(Control).filter(Control.framework_id == fw.id).count()
            if count == 0:
                 # Minimal seed so it's not empty
                 seed_sample_controls(db, fw.id, [f"{fw.code}-1: Placeholder Control"])

    except Exception as e:
        print(f"[STARTUP SEED] CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
