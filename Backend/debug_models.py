from app.database import SessionLocal
from app.models.control import Control
from app.models.process import SubProcess, Process
from sqlalchemy.orm import joinedload
import sys

try:
    db = SessionLocal()
    print("Checking Control model attributes...")
    if hasattr(Control, 'sub_processes'):
        print("PASS: Control.sub_processes exists (via backref)")
    else:
        print("FAIL: Control.sub_processes DOES NOT EXIST")
        # Loop through mapper to see if it's there but not on class
        from sqlalchemy import inspect
        mapper = inspect(Control)
        if 'sub_processes' in mapper.relationships:
             print("PASS: sub_processes is in Mapper relationships")
        else:
             print("FAIL: sub_processes is NOT in Mapper relationships")

    print("\nTesting Query with joinedload AND filters...")
    try:
        from sqlalchemy import or_
        tenant_uuid = "a61624c9-b0d9-4125-9bd5-edf7af8fb78e" # Hardcoded valid UUID
        default_tenant_uuid = "default_tenant"
        
        query = db.query(Control).filter(
            or_(
                Control.tenant_id == tenant_uuid,
                Control.tenant_id == default_tenant_uuid
            )
        )
        
        # Add the options
        query = query.options(
            joinedload(Control.sub_processes).joinedload(SubProcess.process)
        ).order_by(Control.control_id).limit(10)
        
        print(f"Query SQL: {query}")
        results = query.all()
        print(f"PASS: Query executed successfully. Rows: {len(results)}")
        for r in results:
             print(f" - {r.control_id} [{r.status}]: {r.title}")
             
    except Exception as e:
        print(f"FAIL: Query failed - {e}")
        import traceback
        traceback.print_exc()

except Exception as e:
    print(f"Global Error: {e}")
finally:
    pass
