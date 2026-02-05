import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "."))

from app.database import Base
from app.config import settings
from app.models.control import Control
from app.models.framework import Framework
from app.models.process import Process, SubProcess, process_control_mapping

# Constants
TARGET_TENANT_ID = "a61624c9-b0d9-4125-9bd5-edf7af8fb78e"
FRAMEWORK_CODE = "ISO27001"
MISSING_ID = "6.3"
MISSING_TITLE = "6.3 Planning of changes"
MISSING_DESC = "Planning of changes"
TARGET_PROCESS = "Incident & Resilience" # consistent with previous map

def add_missing_control():
    print(f"[-] Adding missing control {MISSING_ID}...")
    
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Get Framework
        fw = db.query(Framework).filter(Framework.code == FRAMEWORK_CODE).first()
        if not fw:
            print("Framework not found")
            return

        # Check if exists
        exists = db.query(Control).filter(
            Control.control_id == MISSING_ID, 
            Control.tenant_id == TARGET_TENANT_ID,
            Control.framework_id == fw.id
        ).first()
        
        if exists:
            print(f"[!] Control {MISSING_ID} already exists.")
            return

        # Get Process
        proc = db.query(Process).filter(Process.name == TARGET_PROCESS).first()
        if not proc:
            print(f"Process {TARGET_PROCESS} not found.")
            return

        # Create Control
        c = Control(
            control_id=MISSING_ID,
            title=MISSING_TITLE,
            description=MISSING_DESC,
            status="not_started",
            framework_id=fw.id,
            category=TARGET_PROCESS,
            tenant_id=TARGET_TENANT_ID
        )
        db.add(c)
        db.commit()
        db.refresh(c)
        
        # Link
        sp = db.query(SubProcess).filter(SubProcess.process_id == proc.id, SubProcess.name == "Controls").first()
        if not sp:
             sp = SubProcess(name="Controls", process_id=proc.id)
             db.add(sp)
             db.commit()
             db.refresh(sp)
             
        db.execute(process_control_mapping.insert().values(subprocess_id=sp.id, control_id=c.id))
        db.commit()
        
        print(f"[+] SUCCESS: Added control {MISSING_ID}.")

    except Exception as e:
        print(f"[!] Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_missing_control()
