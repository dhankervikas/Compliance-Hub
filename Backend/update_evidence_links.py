from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.control import Control
from app.services.policy_intents import POLICY_CONTROL_MAP

def update_links():
    db = SessionLocal()
    try:
        print("Debugging Policy Map Logic...")
        
        # 1. Build Map
        control_policy_map = {}
        target_controls = ["CC6.1", "CC6.2", "CC1.2"]
        
        for policy_name, controls in POLICY_CONTROL_MAP.items():
            normalized_key = policy_name.upper().replace(" ", "_").replace("&", "AND").replace("-", "_")
            for cid in controls:
                if cid not in control_policy_map:
                    control_policy_map[cid] = normalized_key
        
        # 2. Update ALL Matching Controls in DB
        print("\nUpdating ALL Controls in Database...")
        # Fetch all controls that have an ID in our map
        all_mapped_ids = list(control_policy_map.keys())
        controls = db.query(Control).filter(Control.control_id.in_(all_mapped_ids)).all()
        
        count = 0
        for c in controls:
            link_key = control_policy_map[c.control_id]
            note = f"LINK_ID: {link_key}"
            
            # Check if need update
            if not c.implementation_notes or "LINK_ID:" not in c.implementation_notes:
                if c.implementation_notes:
                    c.implementation_notes += f" | {note}"
                else:
                    c.implementation_notes = note
                
                db.add(c)
                count += 1
                if count % 10 == 0:
                    print(f"  - Tagged {c.control_id} -> {link_key}")

        db.commit()
        print(f"\n[Success] Injected LINK_ID tags into {count} controls.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    update_links()
