from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.config import settings
from app.models.control import Control
from app.models.process import Process, SubProcess
from app.models.framework import Framework

# Setup DB
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def remap_change_planning():
    print("[-] Remapping Clause 6.3 to Governance & Policy...")
    
    # Get ISO Framework
    iso = db.query(Framework).filter(Framework.code.like("ISO27001%")).first()
    if not iso:
        print("ISO Framework not found")
        return

    # Target Mapping
    TARGET_PROCESS = "Governance & Policy"
    
    # Find Control 6.3
    c = db.query(Control).filter(
        Control.framework_id == iso.id,
        Control.control_id == "6.3"
    ).first()
    
    if not c:
        print("Control 6.3 not found")
        return
        
    # Find Target Process
    target_process = db.query(Process).filter(Process.name == TARGET_PROCESS).first()
    if not target_process:
        print(f"Target process {TARGET_PROCESS} not found")
        # Fallback create? Should exist.
        return

    # Create/Find SubProcess
    sp_name = f"Intent: {c.title}"[:100]
    
    sp = db.query(SubProcess).filter(
        SubProcess.process_id == target_process.id,
        SubProcess.name == sp_name
    ).first()
    
    if not sp:
        sp = SubProcess(name=sp_name, process_id=target_process.id)
        db.add(sp)
        db.flush()
        
    # Clear existing sub_processes (Remap)
    c.sub_processes = [sp]
    
    db.commit()
    print(f"[+] Successfully remapped Clause 6.3 to {TARGET_PROCESS}")

if __name__ == "__main__":
    remap_change_planning()
