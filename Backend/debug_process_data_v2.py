from app.database import SessionLocal
from app.models.process import Process
from app.models.universal_intent import UniversalIntent
from app.models.intent_framework_crosswalk import IntentFrameworkCrosswalk
from app.models.control import Control

def debug_data():
    db = SessionLocal()
    try:
        print("--- PROCESSES (Top 30) ---")
        procs = db.query(Process).limit(30).all()
        for p in procs:
            print(f"ID: {p.id}, Name: {p.name}, FW: {p.framework_code}")

        print("\n--- UNIVERSAL INTENTS (Sample) ---")
        # Trying 'intent' or 'description' or printing dir
        intents = db.query(UniversalIntent).limit(10).all()
        if intents:
            print(f"Sample Intent Attributes: {intents[0].__dict__.keys()}")
            for i in intents:
                # Assuming 'intent' based on common naming, or 'description'
                txt = getattr(i, 'intent', getattr(i, 'description', 'N/A'))
                cat = getattr(i, 'category', 'N/A')
                print(f"ID: {i.id}, Category: {cat}, Text: {txt}")
        else:
            print("No Universal Intents found.")

        print("\n--- CONTROLS (Governance vs Operations) ---")
        # Check specific controls
        ctrls = db.query(Control).filter(Control.control_id.in_(['A.8.13', 'A.5.24', 'A.5.37'])).all()
        for c in ctrls:
             print(f"Control: {c.control_id} - {c.title}, Cat: {c.category}")

        print("\n--- CONTROL CATEGORY COUNTS ---")
        cats = db.query(Control.category).distinct().all()
        for (cat,) in cats:
            count = db.query(Control).filter(Control.category == cat).count()
            print(f"Category: {cat}, Count: {count}")

    finally:
        db.close()

if __name__ == "__main__":
    debug_data()
