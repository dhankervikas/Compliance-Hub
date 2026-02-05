from app.database import SessionLocal
from app.models.intent_framework_crosswalk import IntentFrameworkCrosswalk
from app.models.universal_intent import UniversalIntent
from app.models.control import Control
from app.models.process import Process

def inspect_mappings():
    db = SessionLocal()
    print("--- DEBUGGING MAPPINGS ---")
    
    # Check Crosswalk Count
    cw_count = db.query(IntentFrameworkCrosswalk).count()
    print(f"Total Crosswalk Entries: {cw_count}")
    
    # Check Intents
    ui_count = db.query(UniversalIntent).count()
    print(f"Total Universal Intents: {ui_count}")
    
    # Check Specific Mapping (e.g. 4.1)
    print("\n--- CHECKING 4.1 MAPPING ---")
    c = db.query(Control).filter(Control.control_id == "4.1").first()
    if c:
        print(f"Control 4.1 Found: ID={c.id}")
    else:
        print("Control 4.1 NOT FOUND")
        
    intent = db.query(UniversalIntent).filter(UniversalIntent.intent_id == "INT-4.1").first()
    if intent:
        print(f"Intent INT-4.1 Found: ID={intent.id}, Category='{intent.category}'")
        
        cw = db.query(IntentFrameworkCrosswalk).filter(IntentFrameworkCrosswalk.intent_id == intent.id).all()
        print(f"Crosswalks for INT-4.1: {len(cw)}")
        for x in cw:
            print(f"  - FW: {x.framework_id}, Ref: {x.control_reference}")
            
    else:
        print("Intent INT-4.1 NOT FOUND")

    # Check Process
    print("\n--- CHECKING PROCESS 'Governance & Policy' ---")
    proc = db.query(Process).filter(Process.name == "Governance & Policy").first()
    if proc:
        print(f"Process Found: ID={proc.id}, Name='{proc.name}'")
    else:
        print("Process 'Governance & Policy' NOT FOUND")
        
    db.close()

if __name__ == "__main__":
    inspect_mappings()
