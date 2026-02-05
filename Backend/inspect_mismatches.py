from app.database import SessionLocal
from app.models.control import Control
from app.models.framework import Framework
from app.models.intent_framework_crosswalk import IntentFrameworkCrosswalk
import sqlalchemy

def inspect_controls():
    db = SessionLocal()
    print("--- INSPECTING CONTROLS & LINKS ---")
    
    fw = db.query(Framework).filter(Framework.code == "ISO27001").first()
    print(f"Framework: ISO27001, ID={fw.id}")
    
    controls = db.query(Control).filter(Control.framework_id == fw.id).all()
    print(f"Total Controls: {len(controls)}")
    
    # Check for whitespace
    whitespace_count = 0
    sample_ws = []
    
    for c in controls:
        if c.control_id != c.control_id.strip():
            whitespace_count += 1
            if len(sample_ws) < 5:
                sample_ws.append(f"'{c.control_id}'")
                
    print(f"Controls with whitespace: {whitespace_count}")
    if sample_ws:
        print(f"  Samples: {', '.join(sample_ws)}")
        
    # Check Crosswalk Match
    cw = db.query(IntentFrameworkCrosswalk).filter(
        IntentFrameworkCrosswalk.framework_id == "ISO27001",
        IntentFrameworkCrosswalk.control_reference == "4.1"
    ).first()
    
    if cw:
        print(f"Crosswalk for 4.1 exists. Ref='{cw.control_reference}'")
        
        # Check Link
        match = db.query(Control).filter(
            Control.framework_id == fw.id,
            Control.control_id == cw.control_reference
        ).first()
        
        if match:
            print("  -> DIRECT MATCH SUCCESS")
        else:
            print("  -> DIRECT MATCH FAILED (Probable cause)")
            # Try strip match
            strip_match = db.query(Control).filter(
                Control.framework_id == fw.id,
                Control.control_id.like(f"{cw.control_reference}%") # simplistic
            ).all()
            print(f"  -> Found {len(strip_match)} matches with LIKE '{cw.control_reference}%'")
            for m in strip_match:
                print(f"     Candidate: '{m.control_id}'")
            
    db.close()

if __name__ == "__main__":
    inspect_controls()
