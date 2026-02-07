from app.database import SessionLocal
from app.models.process import Process
from app.models.universal_intent import UniversalIntent
from app.models.intent_framework_crosswalk import IntentFrameworkCrosswalk
from app.models.control import Control

def debug_data():
    db = SessionLocal()
    try:
        print("--- PROCESSES ---")
        procs = db.query(Process).all()
        for p in procs:
            print(f"ID: {p.id}, Name: {p.name}, FW: {p.framework_code}")
            
        print("\n--- UNIVERSAL INTENTS (Sample) ---")
        intents = db.query(UniversalIntent).limit(20).all()
        for i in intents:
            print(f"ID: {i.id}, Category: {i.category}, Text: {i.intent_text}")

        print("\n--- CROSSWALKS (Sample) ---")
        cws = db.query(IntentFrameworkCrosswalk).limit(20).all()
        for cw in cws:
            print(f"IntentID: {cw.intent_id}, Ref: {cw.control_reference}, FW: {cw.framework_id}")

        print("\n--- CONTROLS (Governance vs Operations check) ---")
        gov_ctrls = db.query(Control).filter(Control.category == "Governance").count()
        ops_ctrls = db.query(Control).filter(Control.category == "Operations").count()
        print(f"Governance Controls: {gov_ctrls}")
        print(f"Operations Controls: {ops_ctrls}")

    finally:
        db.close()

if __name__ == "__main__":
    debug_data()
