from app.database import SessionLocal
from app.models.process import Process
from app.api.processes import get_processes
from unittest.mock import MagicMock
import json

def debug_api():
    db = SessionLocal()
    print("--- DEBUGGING API RESPONSE LOGIC DIRECTLY ---")
    
    # Mock user and dependency
    # get_processes(framework_code, db, current_user)
    
    class MockUser:
        tenant_id = "default_tenant"
        id = "user_1"
    
    try:
        # Call the actual route logic
        # Note: We need to handle the fact that get_processes is an async definition or normal?
        # It's defined as `def get_processes(...)` in the file view I saw earlier.
        
        response = get_processes(framework_code="ISO27001", db=db, current_user=MockUser())
        
        for p in response:
            # print(f"Process: {p.name}")
            for sp in p.sub_processes:
                for c in sp.controls:
                    # Check any clause 4
                    if c.control_id.startswith("4."):
                         found_4_1 = True
                         print(f"FOUND {c.control_id} in P: '{p.name}' / SP: '{sp.name}'")
                         print(f"   -> Title: {c.title}")
                         print(f"   -> Actionable Title: {c.actionable_title}")
                         print(f"   -> Description: {c.description}")
                         print(f"   -> Framework ID: {c.framework_id}")
                         print(f"   -> DB ID: {c.id}")
        
        if not found_4_1:
            print("Control 4.1 NOT FOUND in API Response.")
            
    except Exception as e:
        print(f"API Error: {e}")
        import traceback
        traceback.print_exc()
        
    db.close()

if __name__ == "__main__":
    debug_api()
