from app.database import SessionLocal
from app.models.control import Control
from app.models.process import Process, SubProcess, process_control_mapping
from app.models.intent_framework_crosswalk import IntentFrameworkCrosswalk
from app.models.framework import Framework
from sqlalchemy import text

def cleanse_and_rebuild():
    db = SessionLocal()
    print("--- STARTING ISO DATA CLEANSE ---")
    
    # 1. Get Framework ID
    fw = db.query(Framework).filter(Framework.code == "ISO27001").first()
    if not fw:
        print("Framework not found.")
        return
    fw_id = fw.id
    
    # 2. DELETE CROSSWALK MAPPINGS (Remove Actionable Title Overrides)
    print("Deleting Intent Framework Crosswalks for ISO...")
    db.query(IntentFrameworkCrosswalk).filter(IntentFrameworkCrosswalk.framework_id == 13).delete() # Hardcoded 13 based on earlier logs
    db.query(IntentFrameworkCrosswalk).filter(IntentFrameworkCrosswalk.framework_id == fw_id).delete()
    db.commit()
    
    # 3. DELETE PROCESS MAPPINGS
    print("Clearing Process Mappings...")
    # We iterate processes and clear controls association
    processes = db.query(Process).filter(Process.framework_code == "ISO27001").all()
    for p in processes:
        for sp in p.sub_processes:
            sp.controls = [] # SQLAlchemy handles M2M delete
    db.commit()
    
    # 4. FIX MAPPING LOGIC (Strict)
    print("Re-mapping Controls to Canonical Processes...")
    
    # Define Canonical map based on User Screenshot / Standard
    # 4 -> Context (Governance)
    # 5 -> Leadership (Governance)
    # 6 -> Planning (Governance)
    # 7 -> Support (HR / IT) for now map to "Support" process
    # 8 -> Operation (IT)
    # 9 -> Performance (Governance)
    # 10 -> Improvement (Governance)
    
    # Let's map strictly to "Governance & Policy" for 4, 5, 6, 9, 10 to match User Screenshot 1
    
    gov_proc = db.query(Process).filter(Process.name == "Governance & Policy").first()
    if not gov_proc:
        gov_proc = Process(name="Governance & Policy", framework_code="ISO27001")
        db.add(gov_proc)
        db.commit()
        
    # Ensure SubProcesses exist
    sp_context = get_or_create_sp(db, gov_proc, "Clause 4: Context of the Organization")
    sp_lead = get_or_create_sp(db, gov_proc, "Clause 5: Leadership")
    sp_plan = get_or_create_sp(db, gov_proc, "Clause 6: Planning")
    sp_perf = get_or_create_sp(db, gov_proc, "Clause 9: Performance Evaluation")
    sp_imp = get_or_create_sp(db, gov_proc, "Clause 10: Improvement")
    
    controls = db.query(Control).filter(Control.framework_id == fw_id).all()
    
    for c in controls:
        cid = c.control_id
        target_sp = None
        
        if cid.startswith("4."): target_sp = sp_context
        elif cid.startswith("5."): target_sp = sp_lead
        elif cid.startswith("6."): target_sp = sp_plan
        elif cid.startswith("9."): target_sp = sp_perf
        elif cid.startswith("10."): target_sp = sp_imp
        
        if target_sp:
            target_sp.controls.append(c)
            print(f"Mapped {cid} -> {target_sp.name}")
            
    db.commit()
    print("--- CLEANSE COMPLETE ---")
    db.close()

def get_or_create_sp(db, process, name):
    sp = db.query(SubProcess).filter(SubProcess.process_id == process.id, SubProcess.name == name).first()
    if not sp:
        sp = SubProcess(name=name, process_id=process.id)
        db.add(sp)
        db.commit()
    return sp

if __name__ == "__main__":
    cleanse_and_rebuild()
