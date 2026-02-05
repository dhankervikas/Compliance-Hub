from app.database import SessionLocal
from app.models.control import Control
from app.models.process import Process, SubProcess, process_control_mapping
from sqlalchemy import text

def fix_mapping():
    db = SessionLocal()
    print("--- FIXING 4.1 MAPPING ---")
    
    # 1. Get Control 4.1
    c = db.query(Control).filter(Control.control_id == "4.1").first()
    if not c:
        print("Control 4.1 not found!")
        return
        
    print(f"Control 4.1 ID: {c.id} | Current Title: {c.title}")
    
    # 2. Get Governance Process & SubProcess
    # We need a subprocess to map to. "Governance & Policy" -> "Information Security Policy" or similar.
    # Let's find a subprocess named "Context" or create one in "Governance".
    
    proc = db.query(Process).filter(Process.name.like("Governance%")).first()
    if not proc:
        print("Governance process not found. Creating...")
        proc = Process(name="Governance & Policy", framework_code="ISO27001")
        db.add(proc)
        db.commit()
        
    sub_proc = db.query(SubProcess).filter(SubProcess.process_id == proc.id, SubProcess.name == "Context of the Organization").first()
    if not sub_proc:
        print("Creating 'Context' SubProcess...")
        sub_proc = SubProcess(name="Context of the Organization", process_id=proc.id)
        db.add(sub_proc)
        db.commit()
    
    # 3. Check existing mapping
    # Using SQL directly for M2M table
    # But SqlAlchemy relationship `sub_proc.controls` is easier
    
    if c not in sub_proc.controls:
        print("Mapping 4.1 to SubProcess 'Context'...")
        sub_proc.controls.append(c)
        db.commit()
    else:
        print("4.1 already mapped to 'Context'.")
        
    # 4. Force Title Update Again just to be sure
    c.title = "Determine Context & Stakeholders"
    c.description = "Determine internal and external issues relevant to the ISMS."
    db.commit()
    
    print("--- MAPPING FIXED. ---")
    db.close()

if __name__ == "__main__":
    fix_mapping()
