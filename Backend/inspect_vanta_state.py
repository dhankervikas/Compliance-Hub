from app.database import SessionLocal
from app.models.control import Control
from app.models.framework import Framework
from app.models.process import Process, SubProcess
import sqlalchemy

def inspect_system_state():
    db = SessionLocal()
    print("--- INSPECTING SYSTEM STATE ---")
    
    # Check Frameworks
    fw = db.query(Framework).filter(Framework.code == "ISO27001").first()
    if fw:
        count = db.query(Control).filter(Control.framework_id == fw.id).count()
        print(f"ISO 27001 Control Count: {count} (Expected ~100-110)")
        
        # Breakdown by prefix to see where the 791 comes from
        controls = db.query(Control).filter(Control.framework_id == fw.id).all()
        prefixes = {}
        for c in controls:
            prefix = c.control_id.split('.')[0] if c.control_id else "None"
            prefixes[prefix] = prefixes.get(prefix, 0) + 1
        
        print("Prefix Distribution (Top 10):")
        sorted_prefixes = sorted(prefixes.items(), key=lambda item: item[1], reverse=True)[:10]
        for p, c in sorted_prefixes:
            print(f"  {p}: {c}")

    # Check Processes
    proc_count = db.query(Process).count()
    print(f"\nExisting Processes: {proc_count}")
    processes = db.query(Process).all()
    for p in processes:
        print(f"  - {p.name} ({p.framework_code})")

    db.close()

if __name__ == "__main__":
    inspect_system_state()
