from app.database import SessionLocal
from app.models.person import Person
from app.models.process import Process, SubProcess
from app.models.framework import Framework
from app.models.control import Control
from app.api.processes import get_processes
from unittest.mock import MagicMock

db = SessionLocal()

print("--- DEBUGGING API LOGIC ---")

# 1. Check Framework Code
fw = db.query(Framework).filter(Framework.code.like('%ISO%')).first()
print(f"DB Framework: Code='{fw.code}', ID={fw.id}")

# 2. Check Process Data
proc = db.query(Process).filter(Process.name == "Information Security").first()
if proc:
    print(f"DB Process: Name='{proc.name}', FrameworkCode='{proc.framework_code}'")
    for sp in proc.sub_processes:
        print(f"  > SubProcess: '{sp.name}', Controls Count (DB)={len(sp.controls)}")
else:
    print("CRITICAL: Process 'Information Security' not found in DB!")

# 3. Simulate API Call
# Mock User
current_user = MagicMock()
current_user.tenant_id = "default_tenant" # Assumption

print(f"\n--- Simulating API Call for code='{fw.code}' ---")
try:
    # We call the logic manually or just inspect query logic
    # Let's manual-query what the API querying does
    
    # API Filter 1: Process.framework_code == input_code
    # If input is 'ISO27001' and DB is 'ISO27001', match.
    api_processes = db.query(Process).filter(Process.framework_code == "ISO27001").all()
    print(f"API Query (code='ISO27001') found {len(api_processes)} processes.")
    
    if api_processes:
        p = api_processes[0]
        sp = p.sub_processes[0]
        controls = sp.controls
        print(f"  Process '{p.name}' -> SubProcess '{sp.name}' has {len(controls)} controls attached.")
        
        # API Filter 2: Control Framework ID
        target_fw_id = fw.id
        filtered_controls = [c for c in controls if c.framework_id == target_fw_id]
        print(f"  After Framework ID Filter (fw_id={target_fw_id}): {len(filtered_controls)} controls remain.")
        
        # API Filter 3: Tenant
        # This is likely where it fails if Tenant IDs don't match
        # Let's inspect first control tenant
        if filtered_controls:
            c = filtered_controls[0]
            print(f"  Sample Control Tenant ID: '{c.tenant_id}'")

except Exception as e:
    print(f"Error during simulation: {e}")

db.close()
