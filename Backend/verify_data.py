from app.database import SessionLocal
from app.models.process import Process
from app.models.control import Control
from app.models.intent_framework_crosswalk import IntentFrameworkCrosswalk
from app.models.universal_intent import UniversalIntent
from app.models.person import Person # Fix for Mapper Registry

db = SessionLocal()

print("--- VERIFICATION REPORT ---")

# 1. Check Processes
procs = db.query(Process).filter(Process.framework_code == "ISO27001").all()
print(f"Total ISO 27001 Processes: {len(procs)}")
names = sorted([p.name for p in procs])
print("Process List:")
for n in names:
    print(f" - {n}")

# 2. Check a Sample Control (A.5.1)
control_ref = "A.5.1"
c = db.query(Control).filter(Control.control_id == control_ref, Control.framework_id == 1).first()
if c:
    print(f"\nControl {c.control_id}: {c.title}")
    print(f" - Status: {c.status}")
    print(f" - Category (on Control): {c.category}")
    
    # Check Crosswalk
    cw = db.query(IntentFrameworkCrosswalk).filter(
        IntentFrameworkCrosswalk.control_reference == control_ref,
        IntentFrameworkCrosswalk.framework_id == "ISO27001"
    ).all()
    
    print(f" - Mapped Intents ({len(cw)}):")
    for x in cw:
        ui = db.query(UniversalIntent).filter(UniversalIntent.id == x.intent_id).first()
        print(f"   -> {ui.intent_id} ({ui.status}): {ui.description[:50]}... [Cat: {ui.category}]")
else:
    print(f"Control {control_ref} not found.")

db.close()
