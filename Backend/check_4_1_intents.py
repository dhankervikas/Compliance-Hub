from app.database import SessionLocal
from app.models.universal_intent import UniversalIntent
from app.models.intent_framework_crosswalk import IntentFrameworkCrosswalk
from app.models.control import Control

def check_intents():
    db = SessionLocal()
    print("--- CHECKING INTENTS FOR 4.1 ---")
    
    # 1. Find Control 4.1
    c = db.query(Control).filter(Control.control_id == "4.1").first()
    if not c:
        print("Control 4.1 not found.")
        return

    print(f"Control 4.1 Title: {c.title}")
    
    # 2. Find Crosswalk
    links = db.query(IntentFrameworkCrosswalk).filter(
        IntentFrameworkCrosswalk.control_reference == "4.1",
        IntentFrameworkCrosswalk.framework_id == 13 # ISO
    ).all()
    
    print(f"Found {len(links)} linked intents.")
    
    for link in links:
        intent = db.query(UniversalIntent).filter(UniversalIntent.id == link.intent_id).first()
        if intent:
            print(f"   -> Intent ID: {intent.id}")
            print(f"   -> Description (Action Title): {intent.description}")
            print(f"   -> Status: {intent.status}")
            
    db.close()

if __name__ == "__main__":
    check_intents()
