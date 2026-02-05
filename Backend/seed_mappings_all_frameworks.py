from app.database import SessionLocal
from app.models.control import Control
from app.models.process import SubProcess

def seed_all_mappings():
    db = SessionLocal()
    try:
        print("Starting Universal Mapping Seed...")
        
        # Helper to find subprocess
        def get_sp(name_part):
            return db.query(SubProcess).filter(SubProcess.name.ilike(f"%{name_part}%")).first()

        sp_governance = get_sp("Governance") or get_sp("Policy")
        sp_risk = get_sp("Risk")
        sp_ops = get_sp("Security Monitoring")
        sp_access = get_sp("Access Management")

        # Map All Frameworks > 1 (ISO 27001 is already done)
        controls = db.query(Control).filter(Control.framework_id > 1).all()
        print(f"Found {len(controls)} controls for other frameworks.")

        count = 0
        for c in controls:
            target_sp = sp_governance # Default fallthrough
            
            # Simple Heuristics for SOC 2 / NIST
            cid = c.control_id.upper()
            title = c.title.lower() if c.title else ""

            if "RISK" in title: target_sp = sp_risk
            if "ACCESS" in title or "LOGICAL" in title: target_sp = sp_access
            if "OPERATION" in title or "MONITOR" in title: target_sp = sp_ops
            
            if target_sp and c not in target_sp.controls:
                target_sp.controls.append(c)
                count += 1
        
        db.commit()
        print(f"Successfully mapped {count} additional controls (SOC2/NIST).")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_all_mappings()
