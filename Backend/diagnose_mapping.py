from app.database import SessionLocal
from app.models.process import Process, SubProcess
from app.models.control import Control
from app.models.person import Person # Fix Registry
from sqlalchemy import func

def diagnose_state():
    db = SessionLocal()
    print("--- DIAGNOSTIC REPORT ---")
    
    # 1. PROCESSES
    procs = db.query(Process).filter(Process.framework_code == "ISO27001").all()
    print(f"Total ISO 27001 Processes: {len(procs)}")
    for p in procs:
        # Count Controls via SubProcess
        count = 0
        for sp in p.sub_processes:
            count += len(sp.controls)
        print(f" - [{p.id}] {p.name}: {count} Controls")
        
    # 2. ORPHANS
    # Controls with NO subprocess
    from app.models.process import process_control_mapping
    
    mapped_ids = db.query(process_control_mapping.c.control_id).distinct()
    orphans = db.query(Control).filter(
        Control.framework_id == 1,
        ~Control.id.in_(mapped_ids)
    ).count()
    
    print(f"\nOrphaned ISO Controls (No Process): {orphans}")
    
    db.close()

if __name__ == "__main__":
    diagnose_state()
