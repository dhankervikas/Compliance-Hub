
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from app.database import Base
from app.config import settings
from app.models.control import Control
from app.models.process import SubProcess, Process
from app.schemas.control import Control as ControlSchema

# Setup Path
sys.path.append(os.path.join(os.path.dirname(__file__), "."))

# Setup DB
print(f"Connecting to {settings.DATABASE_URL}")
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def verify_process_data():
    print("[-] Verifying Control -> Process Mappings...")
    
    # query with eager loading (simulating API)
    # Join SubProcess to filter
    controls = db.query(Control).join(Control.sub_processes).options(
        joinedload(Control.sub_processes).joinedload(SubProcess.process)
    ).limit(5).all()
    
    if not controls:
        print("No controls found!")
        return
        
    for c in controls:
        print(f"Control: {c.control_id}")
        print(f"  - Process Name (Prop): {c.process_name}")
        print(f"  - SubProcess Name (Prop): {c.sub_process_name}")
        
        # Verify Schema serialization
        try:
            schema = ControlSchema.from_orm(c)
            print(f"  - Schema Process: {schema.process_name}")
            print(f"  - Schema SubProcess: {schema.sub_process_name}")
        except Exception as e:
            print(f"  - Schema Error: {e}")
            
    print("\n[SUCCESS] Verification Complete")

if __name__ == "__main__":
    verify_process_data()
