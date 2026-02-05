from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.control import Control
from app.models.evidence import Evidence
from app.api.processes import get_actionable_title, ACTIONABLE_TITLES

def verify_inheritance():
    db: Session = SessionLocal()
    try:
        print("--- VERIFYING INHERITANCE MAP ---")
        
        # 1. Check Mappings
        iso_id = "A.5.1"
        soc_id = "CC1.1"
        
        iso_title = ACTIONABLE_TITLES.get(iso_id)
        soc_title = ACTIONABLE_TITLES.get(soc_id)
        
        print(f"ISO {iso_id} -> {iso_title}")
        print(f"SOC {soc_id} -> {soc_title}")
        
        if iso_title == soc_title:
            print("[OK] SUCCESS: ISO and SOC match on Intent!")
        else:
            print("[FAIL] FAILURE: Titles do not match.")
            return

        # 2. Check DB Controls
        print("\n--- CHECKING DB CONTROLS ---")
        iso_ctrl = db.query(Control).filter(Control.control_id == iso_id).first()
        soc_ctrl = db.query(Control).filter(Control.control_id == soc_id).first()
        
        if not iso_ctrl:
            print(f"[WARN] Warning: Control {iso_id} not found in DB.")
        if not soc_ctrl:
            print(f"[WARN] Warning: Control {soc_id} not found in DB.")
            
        if iso_ctrl and soc_ctrl:
            print(f"Found ISO Control ID: {iso_ctrl.id} (Tenant: {iso_ctrl.tenant_id})")
            print(f"Found SOC Control ID: {soc_ctrl.id} (Tenant: {soc_ctrl.tenant_id})")
            
            # 3. Simulate Logic
            print("\n--- SIMULATING SYNC LOGIC ---")
            ctrl_a = iso_ctrl
            ctrl_b = soc_ctrl
            
            title_a = get_actionable_title(ctrl_a)
            print(f"Control A Actionable Title: {title_a}")
            
            # Logic from evidence.py
            sync_key = title_a
            matching_ids = [cid for cid, t in ACTIONABLE_TITLES.items() if t == sync_key]
            print(f"Matching Control IDs in Map: {matching_ids}")
            
            if soc_id in matching_ids:
                 print("[OK] SUCCESS: SOC ID found in matching list.")
            else:
                 print("[FAIL] FAILURE: SOC ID not found in matching list.")

    finally:
        db.close()

if __name__ == "__main__":
    verify_inheritance()
