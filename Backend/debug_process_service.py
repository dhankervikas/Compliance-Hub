from app.database import SessionLocal
from app.services.process_service import ProcessService
from app.models.framework import Framework

def debug_service():
    db = SessionLocal()
    print("--- DEBUGGING PROCESS SERVICE ---")
    
    fw_code = "ISO27001"
    
    # 1. Check Framework
    fw = db.query(Framework).filter(Framework.code == fw_code).first()
    print(f"Framework: {fw.code} (ID: {fw.id})")
    
    # 2. Call Service directly
    print("\nCalling ProcessService.get_processes_with_controls...")
    results = ProcessService.get_processes_with_controls(db, fw_code)
    
    print(f"\nService returned {len(results)} processes.")
    
    for p in results:
        print(f"Process: {p['name']}")
        print(f"  Controls: {len(p['controls'])}")
        if p['name'] == "Governance & Policy":
            print("  [Deep Dive: Governance & Policy]")
            # Re-enact logic to see where it fails
            from app.models.universal_intent import UniversalIntent
            from app.models.intent_framework_crosswalk import IntentFrameworkCrosswalk
            from app.models.control import Control
            
            intents = db.query(UniversalIntent).filter(UniversalIntent.category == p['name']).all()
            print(f"  - Intents found: {len(intents)}")
            intent_ids = [i.id for i in intents]
            print(f"  - Intent IDs: {intent_ids[:5]}...")
            
            crosswalks = db.query(IntentFrameworkCrosswalk).filter(
                IntentFrameworkCrosswalk.intent_id.in_(intent_ids),
                IntentFrameworkCrosswalk.framework_id == fw_code
            ).all()
            print(f"  - Crosswalks found: {len(crosswalks)}")
            control_refs = [cw.control_reference for cw in crosswalks]
            print(f"  - Refs: {control_refs[:5]}...")
            
            controls = db.query(Control).filter(
                Control.framework_id == fw.id,
                Control.control_id.in_(control_refs)
            ).all()
            print(f"  - Controls found via IN query: {len(controls)}")
            
            # Try manual check
            if control_refs:
                c1 = db.query(Control).filter(Control.framework_id == fw.id, Control.control_id == control_refs[0]).first()
                print(f"  - Manual check for '{control_refs[0]}': {c1}")

    db.close()

if __name__ == "__main__":
    debug_service()
