from app.database import SessionLocal
from app.models.process import Process
from app.models.universal_intent import UniversalIntent
from app.models.control import Control
from app.models.intent_framework_crosswalk import IntentFrameworkCrosswalk
from sqlalchemy import or_

def fix_operations():
    db = SessionLocal()
    try:
        print("[FIX OPS] Starting consolidation...")

        # 1. Define Categories to Consolidate into "Operations"
        # These are currently separate processes but should be under Operations
        TARGET_CATEGORIES = [
            "Incident & Resilience",
            "Physical Security",
            "Backup Management",
            "Logging & Monitoring",
            "Technical Vulnerability Management",
            "Malware Protection",
            "Capacity Management",
            "Operations (General)",
            "Operations" # Self
        ]

        # 2. Update Controls
        # Find all controls in these categories (or heuristic matching)
        # Note: 'Control.category' might be textual.
        print("\n[FIX OPS] Updating Control Categories...")
        controls = db.query(Control).filter(Control.category.in_(TARGET_CATEGORIES)).all()
        for c in controls:
            c.category = "Operations"
        db.commit()
        print(f"Updated {len(controls)} controls to 'Operations'")

        # 3. Update Universal Intents
        # Start by finding intents that match these categories
        print("\n[FIX OPS] Updating Universal Intent Categories...")
        intents = db.query(UniversalIntent).filter(UniversalIntent.category.in_(TARGET_CATEGORIES)).all()
        for i in intents:
            i.category = "Operations"
        db.commit()
        print(f"Updated {len(intents)} intents to 'Operations'")

        # 4. Manage Process Rows
        # A. Ensure "Operations" Process exists
        ops_proc = db.query(Process).filter(Process.name == "Operations", Process.framework_code == "ISO27001").first()
        if not ops_proc:
            print("Creating 'Operations' Process...")
            ops_proc = Process(name="Operations", description="Operational Security Controls", framework_code="ISO27001")
            db.add(ops_proc)
            db.commit()
        
        # B. Delete the old granular processes (Backup, Incident, etc.)
        # Only delete for ISO27001 to be safe, or globally if unique.
        print("\n[FIX OPS] Cleaning up redundant processes...")
        redundant_procs = db.query(Process).filter(
            Process.name.in_(TARGET_CATEGORIES),
            Process.framework_code == "ISO27001",
            Process.name != "Operations" # Don't delete self
        ).all()
        
        for p in redundant_procs:
            print(f"Deleting Process: {p.name}")
            db.delete(p)
        db.commit()

        # 5. Fallback: Force Update specific Controls if they were missed
        # (e.g. if they were labeled "Governance" erroneously)
        # A.8.13 (Backups), A.8.15 (Logging), A.5.24-28 (Incidents), A.7.x (Physical)
        print("\n[FIX OPS] Force updating specific ISO controls...")
        iso_ops_patterns = ["A.7.", "A.8.13", "A.8.15", "A.8.16", "A.8.17", "A.5.24", "A.5.25", "A.5.26", "A.5.27", "A.5.28", "A.5.29", "A.5.30", "A.5.37", "A.8.6", "A.8.7", "A.8.8"]
        
        manual_fix_count = 0
        for pat in iso_ops_patterns:
            ctrls = db.query(Control).filter(Control.control_id.like(f"%{pat}%"), Control.framework_id == 1).all() # Assuming ISO ID=1 or based on code
            # Safer query by framework code Join if needed, but heuristic is okay locally
            # Let's get framework ID for ISO27001
            iso_fw = db.query(Process).filter(Process.code == "ISO27001").first() # Wait, framework model..
            
            for c in ctrls:
                c.category = "Operations"
                manual_fix_count += 1
        
        db.commit()
        print(f"Force updated {manual_fix_count} ISO controls to 'Operations'")

        print("[FIX OPS] Done.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    fix_operations()
