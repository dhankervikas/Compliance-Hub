
from app.database import SessionLocal
from app.models.process import Process, SubProcess
from app.models.control import Control
from app.models.user import User

def debug_backend():
    db = SessionLocal()
    try:
        print("DEBUGGING BACKEND LOGIC...")
        
        # 1. Check User Tenant
        user = db.query(User).filter(User.username == "admin").first()
        print(f"User Tenant: {user.tenant_id}")
        
        # 2. Check Process -> SubProcess
        process = db.query(Process).filter(Process.name == "Governance & Policy", Process.framework_code == "ISO27001").first()
        if not process:
            print("Process 'Governance & Policy' not found.")
            return

        print(f"Process: {process.name} (ID: {process.id})")
        
        if not process.sub_processes:
            print("No SubProcesses found.")
            return

        sp = process.sub_processes[0]
        print(f"SubProcess: {sp.name} (ID: {sp.id})")
        
        # 3. Check Relationships
        print(f"Checking Controls for SubProcess {sp.id}...")
        all_controls = sp.controls
        print(f"Raw Controls Count: {len(all_controls)}")
        
        if all_controls:
            c = all_controls[0]
            print(f"Sample Control: {c.control_id} (Tenant: {c.tenant_id})")
            
            # 4. Simulate Filter
            filtered = [c for c in all_controls if c.tenant_id == user.tenant_id]
            print(f"Filtered Controls Count: {len(filtered)}")
        else:
            print("No controls linked via relationship.")
            
            # Check Manually via Join
            from sqlalchemy import text
            res = db.execute(text(f"SELECT COUNT(*) FROM process_control_mapping WHERE subprocess_id = {sp.id}")).fetchone()
            print(f"Manual DB Count for SubProcess {sp.id}: {res[0]}")

    finally:
        db.close()

if __name__ == "__main__":
    debug_backend()
