from app.database import SessionLocal
from app.models.universal_intent import UniversalIntent
from app.models.intent_framework_crosswalk import IntentFrameworkCrosswalk
from app.models.framework import Framework
from app.models.control import Control
from app.models.evidence import Evidence
from app.services.evidence_sync_service import sync_evidence_by_intent

def seed_and_test_gravity():
    db = SessionLocal()
    print("--- SEEDING GRAVITY DATA ---")
    
    # 1. Create Universal Intent
    intent_id = "INTENT_ORG_CONTEXT"
    ui = db.query(UniversalIntent).filter(UniversalIntent.intent_id == intent_id).first()
    if not ui:
        ui = UniversalIntent(
            intent_id=intent_id, 
            description="Understand Organization Context", 
            category="Governance"
        )
        db.add(ui)
        db.commit()
        print(f"Created UI: {intent_id}")
    else:
        print(f"UI {intent_id} exists.")

    db.refresh(ui)

    # 2. Create Mappings (ISO 4.1 <-> SOC2 CC1.1)
    # Ensure Frameworks exist
    iso = db.query(Framework).filter(Framework.code == "ISO27001").first()
    soc = db.query(Framework).filter(Framework.code == "SOC2").first()
    
    if iso and soc:
        # Link ISO 4.1
        if not db.query(IntentFrameworkCrosswalk).filter_by(intent_id=ui.id, framework_id="ISO27001", control_reference="4.1").first():
            db.add(IntentFrameworkCrosswalk(intent_id=ui.id, framework_id="ISO27001", control_reference="4.1"))
            print("Mapped ISO 4.1")

        # Link SOC2 CC1.1 (Assuming CC1.1 exists, else try CC1.0 or similar)
        # Check if CC1.1 exists
        target_ctrl = db.query(Control).filter(Control.control_id == "CC1.1", Control.framework_id == soc.id).first()
        if target_ctrl:
             if not db.query(IntentFrameworkCrosswalk).filter_by(intent_id=ui.id, framework_id="SOC2", control_reference="CC1.1").first():
                db.add(IntentFrameworkCrosswalk(intent_id=ui.id, framework_id="SOC2", control_reference="CC1.1"))
                print("Mapped SOC2 CC1.1")
        else:
            print("Target Control SOC2 CC1.1 not found, skipping SOC mapping.")

        db.commit()
    
    # 3. Simulate Evidence Upload to ISO 4.1
    # Find ISO 4.1 Control
    iso_ctrl = db.query(Control).filter(Control.control_id == "4.1", Control.framework_id == iso.id).first()
    if not iso_ctrl:
        print("ISO 4.1 Control Not Found!")
        return

    print(f"Simulating upload to {iso_ctrl.control_id}...")
    
    # Create Evidence Record
    ev = Evidence(
        filename="org_chart.pdf",
        file_path="/tmp/org_chart.pdf",
        title="Org Chart",
        control_id=iso_ctrl.id,
        master_intent_id=intent_id
    )
    db.add(ev)
    db.commit()
    db.refresh(ev)
    
    print(f"Created Evidence ID {ev.id}")

    # 4. RUN SYNC
    sync_evidence_by_intent(db, ev.id, intent_id)
    
    db.close()

if __name__ == "__main__":
    seed_and_test_gravity()
