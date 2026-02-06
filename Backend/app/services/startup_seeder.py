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
        # 1. SOC 2 (Handled by existing logic, but let's double check existence here too just in case)
        # We rely on seed_soc2_unified called separately, or we can call it here.
        # Let's assume main.py calls seed_soc2_unified separately for deep logic.
        
        # 2. ISO 27001 (Deep Seed)
        # Import the deep seeder
        try:
            import sys
            import os
            # Add Backend root to path to allow importing 'seed_iso27001'
            # Assuming this runs from 'app/' or root. 
            # If running from app/, then '..' is root.
            # But python path usually includes root.
            from seed_iso27001 import main as seed_iso_main
            print("[STARTUP SEED] Running ISO 27001 Deep Seed...")
            seed_iso_main()
        except ImportError:
            print("[STARTUP SEED] Warning: Could not import seed_iso27001. Using fallback creation.")
            seed_frameork_if_missing(db, "ISO27001", "ISO 27001:2022", "Information Security Management", "2022")

        # 3. NIST CSF 2.0 (Deep Seed)
        try:
            from seed_nist_csf import seed_nist
            print("[STARTUP SEED] Running NIST CSF 2.0 Deep Seed...")
            seed_nist()
        except ImportError:
            print("[STARTUP SEED] Warning: Could not import seed_nist_csf. Using fallback.")
            seed_frameork_if_missing(db, "NIST_CSF_2.0", "NIST CSF 2.0", "Cybersecurity Framework", "2.0")

        # 4. Extended Frameworks (Simple Seed)
        EXTENDED_FRAMEWORKS = [
            {"code": "HIPAA", "name": "HIPAA Security Rule", "desc": "Protection of electronic protected health information (ePHI)."},
            {"code": "PCI_DSS_v4", "name": "PCI DSS v4.0", "desc": "Payment Card Industry Data Security Standard."},
            {"code": "ISO_27701", "name": "ISO/IEC 27701:2019", "desc": "Privacy Information Management System (PIMS)."},
            {"code": "ISO_42001", "name": "ISO/IEC 42001:2023", "desc": "Artificial Intelligence Management System (AIMS)."},
            {"code": "GDPR", "name": "GDPR", "desc": "General Data Protection Regulation."},
            {"code": "US_DATA_PRIVACY", "name": "US Data Privacy", "desc": "CCPA, CPRA, and state-level privacy laws."},
            {"code": "NIST_800_53", "name": "NIST SP 800-53 r5", "desc": "Security and Privacy Controls for Information Systems."}
        ]

        SAMPLE_CONTROLS = {
            "HIPAA": ["Access Control", "Audit Controls", "Integrity", "Person or Entity Authentication", "Transmission Security"],
            "PCI_DSS_v4": ["Install Firewalls", "Protect Stored Data", "Encrypt Transmission", "Use Anti-Virus", "Restrict Access"],
            "GDPR": ["Lawfulness of Processing", "Right to Erasure", "Data Portability", "Data Protection Impact Assessment"],
            "ISO_42001": ["AI Risk Assessment", "Data Quality", "AI System Lifecycle", "Transparency and Explainability"]
        }

        for fw_def in EXTENDED_FRAMEWORKS:
            fw = seed_frameork_if_missing(db, fw_def["code"], fw_def["name"], fw_def["desc"], "1.0")
            
            # Seed samples if controls are missing
            existing_ctrls = db.query(Control).filter(Control.framework_id == fw.id).count()
            if existing_ctrls == 0:
                controls = SAMPLE_CONTROLS.get(fw_def["code"], [])
                # If no specific samples, add a generic placeholder
                if not controls:
                    controls = [f"{fw_def['code']} Control 1", f"{fw_def['code']} Control 2"]
                seed_sample_controls(db, fw.id, controls)

    except Exception as e:
        print(f"[STARTUP SEED] CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
