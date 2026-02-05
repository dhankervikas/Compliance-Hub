from app.database import SessionLocal
from app.models.framework import Framework
from app.models.control import Control
from app.models.process import Process, SubProcess
from app.models.person import Person # For safety

db = SessionLocal()
try:
    print("--- Fixing Process Relationships for ISO 27001 ---")
    
    # 1. Get Framework
    fw = db.query(Framework).filter(Framework.code.like('%ISO%')).first()
    if not fw:
        print("ISO Framework not found!")
        exit(1)
        
    print(f"Target Framework: {fw.code} (ID: {fw.id})")
    
    # 2. Get Controls
    controls = db.query(Control).filter(Control.framework_id == fw.id).all()
    print(f"Found {len(controls)} ISO Controls")
    
    if len(controls) == 0:
        print("No controls to map.")
        exit(0)

    # 3. Find or Create Process
    proc = db.query(Process).filter(
        Process.name == "Information Security", 
        Process.framework_code == "ISO27001"
    ).first()
    
    if not proc:
        print("Creating 'Information Security' Process...")
        proc = Process(name="Information Security", description="Core Security Governance", framework_code="ISO27001")
        db.add(proc)
        db.commit()
        db.refresh(proc)
    else:
        print(f"Using existing Process: {proc.name} (ID: {proc.id})")

    # 4. Find or Create SubProcess
    sp = db.query(SubProcess).filter(
        SubProcess.name == "Governance",
        SubProcess.process_id == proc.id
    ).first()
    
    if not sp:
        print("Creating 'Governance' SubProcess...")
        sp = SubProcess(name="Governance", description="Policies and Standards", process_id=proc.id)
        db.add(sp)
        db.commit()
        db.refresh(sp)
    else:
        print(f"Using existing SubProcess: {sp.name} (ID: {sp.id})")
        
    # 5. Link Controls (M2M)
    # We assign all these controls to this subprocess
    # SQLAlchemy handles the association table update
    
    # Check what's already there to avoid duplicates if specific check logic needed, 
    # but .extend() or assignment usually handles uniques in set-like relationships or might duplicate?
    # Safer to overwrite or check.
    
    # Let's just overwrite for this fix to ensure consistency "All ISO -> Governance"
    sp.controls = controls
    db.commit()
    
    print(f"Successfully linked {len(controls)} controls to SubProcess '{sp.name}'.")

except Exception as e:
    print(f"ERROR: {e}")
    db.rollback()
finally:
    db.close()
