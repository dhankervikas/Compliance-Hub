import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "."))

from app.database import Base
from app.config import settings
from app.models.control import Control
from app.models.process import Process, SubProcess, process_control_mapping

# Constants
TARGET_TENANT_ID = "a61624c9-b0d9-4125-9bd5-edf7af8fb78e"

def link_testtest_controls():
    print(f"[-] Starting LINK_TESTTEST_CONTROLS for {TARGET_TENANT_ID}...")
    
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 1. Get Controls for Tenant
        controls = db.query(Control).filter(Control.tenant_id == TARGET_TENANT_ID).all()
        print(f"[-] Found {len(controls)} controls to link.")
        
        # 2. Get Process Map (Global)
        processes = db.query(Process).all()
        proc_map = {p.name: p for p in processes}
        
        mappings_to_add = []
        
        for c in controls:
            if not c.category:
                print(f"[!] Control {c.control_id} has no category. Skipping.")
                continue
                
            # Find Process
            parent_proc = proc_map.get(c.category)
            if not parent_proc:
                # Try partial match or fallback? 
                # For now, strict match.
                # 'Governance & Policy' vs 'Governance' etc.
                continue
                
            # Find/Ensure SubProcess "Controls"
            # Optimization: Load Subprocesses
            sp = db.query(SubProcess).filter(SubProcess.process_id == parent_proc.id, SubProcess.name == "Controls").first()
            if not sp:
                # This should exist from master restore, but if not, create it
                sp = SubProcess(name="Controls", description="Mapped Controls", process_id=parent_proc.id)
                db.add(sp)
                db.commit()
                db.refresh(sp)
                
            # Check if mapping exists
            # We can just batch insert and ignore duplicates if we use `ignore` or check first
            # Checking first is safer for ORM
            # Actually, bulk insert is faster.
            
            mappings_to_add.append({"subprocess_id": sp.id, "control_id": c.id})
            
        print(f"[-] Prepared {len(mappings_to_add)} mappings.")
        
        # 3. Bulk Insert
        if mappings_to_add:
             # De-duplicate list just in case
             unique_mappings = [dict(t) for t in {tuple(d.items()) for d in mappings_to_add}]
             
             # Use Core Insert to avoid overhead
             # But we need to avoid PK violations.
             # Cleanest: Delete existing mappings for these controls FIRST?
             # No, these are new controls. They shouldn't have mappings.
             
             db.execute(process_control_mapping.insert(), unique_mappings)
             db.commit()
             
        print(f"[+] SUCCESS: Linked {len(mappings_to_add)} controls to processes.")
        
    except Exception as e:
        print(f"[!] Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    link_testtest_controls()
