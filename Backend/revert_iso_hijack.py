from app.database import SessionLocal
from app.models.control import Control
from app.models.framework import Framework
from sqlalchemy import or_

def revert_hijack():
    db = SessionLocal()
    try:
        iso = db.query(Framework).filter(Framework.code == "ISO27001").first()
        soc2 = db.query(Framework).filter(Framework.code == "SOC2").first()
        ai = db.query(Framework).filter(Framework.code == "AI_FRAMEWORK").first()
        
        if not ai or not iso or not soc2:
            print("Missing frameworks. Aborting.")
            return
            
        print(f"ISO ID: {iso.id}, SOC2 ID: {soc2.id}, AI ID: {ai.id}")
        
        # 1. Revert ISO Clauses (4.x - 10.x)
        # 2. Revert ISO Annex A (A.x) - Assume all A.x belong to ISO for now unless AI specific?
        #    AI Framework used 'Clause / Control No.'. Check collision.
        #    If AI had 'A.5.1', it stole it.
        #    We assume strict priority: ISO owns "A.x.x". AI should be prefixed.
        
        # Strategies:
        # - Any control in AI framework that starts with '4.', '5.'...'10.' (clauses) -> ISO
        # - Any control in AI framework that starts with 'A.' -> ISO
        # - Any control in AI framework that starts with 'CC', 'PI', 'A1.' -> SOC2
        
        # ISO Revert
        iso_count = 0
        ai_controls = db.query(Control).filter(Control.framework_id == ai.id).all()
        
        for c in ai_controls:
            is_iso = False
            # Check ISO Clauses
            if c.control_id[0].isdigit() and '.' in c.control_id:
                parts = c.control_id.split('.')
                if parts[0].isdigit() and 4 <= int(parts[0]) <= 10:
                    is_iso = True
            
            # Check ISO Annex A
            if c.control_id.startswith("A."):
                is_iso = True
                
            if is_iso:
                print(f"Reverting ISO Control: {c.control_id} ({c.title})")
                c.framework_id = iso.id
                iso_count += 1
                
        # SOC2 Revert
        soc2_count = 0
        # Re-fetch or continue loop?
        # Since we modified memory objects in loop, safer to continue or refetch.
        # But loop is over list, so obj refs are fine.
        
        # Need to be careful. 'A1.' is valid SOC2 (Additional Criteria)? Or 'CC'?
        # Let's target specific SOC2 prefixes: CC, PI, A1, etc.
        # Ref checking seed_soc2.py would confirm prefixes.
        # Typical SOC2: CC1.1, CC1.2, ...
        
        for c in ai_controls: # Using same list, but if we changed framework_id above, it's fine.
            if c.framework_id == iso.id: continue # Already moved
            
            is_soc2 = False
            if c.control_id.startswith("CC") and c.control_id[2].isdigit(): is_soc2 = True
            if c.control_id.startswith("PI") and c.control_id[2].isdigit(): is_soc2 = True
            # A1.1 might collide with ISO Annex A if not careful? 
            # ISO is A.5.1 (A dot). SOC might be A1. (A one dot).
            
            if is_soc2:
                print(f"Reverting SOC2 Control: {c.control_id} ({c.title})")
                c.framework_id = soc2.id
                soc2_count += 1

        db.commit()
        print(f"Reverted {iso_count} controls to ISO 27001.")
        print(f"Reverted {soc2_count} controls to SOC 2.")
        
    finally:
        db.close()

if __name__ == "__main__":
    revert_hijack()
