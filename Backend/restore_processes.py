
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.process import Process, SubProcess
from app.models.control import Control
from app.models.framework import Framework
from sqlalchemy import text

# The 22 Standard Processes (inferred from functional_mapping.json keys + user intent)
STANDARD_PROCESSES = [
    "Governance & Policy",
    "Risk Management",
    "Performance Evaluation",
    "Improvement",
    "Change Management",
    "Supplier Management",
    "Incident & Resilience",
    "HR Security",
    "Access Control (IAM)",
    "Asset Management",
    "Cryptography",
    "Configuration Management",
    "Network Security",
    "Vulnerability Management",
    "Secure Development (SDLC)",
    "Operations", # User confirmed "Operations" is the correct process name
    "Physical Security",
    "Logging & Monitoring",
    "Legal & Compliance",
    "Business Continuity",
    "Data Protection & Privacy",
    "Endpoint Security"
]

CATEGORY_MAP = {
    "Governance": "Governance & Policy",
    "Risk Management": "Risk Management",
    "Performance Evaluation": "Performance Evaluation",
    "Improvement": "Improvement",
    "HR Security": "HR Security",
    "Incident & Resilience": "Incident & Resilience",
    "Asset Management": "Asset Management",
    "Access Control (IAM)": "Access Control (IAM)",
    "Physical Security": "Physical Security",
    "Supplier Mgmt": "Supplier Management",
    "Network Security": "Network Security",
    "Legal & Compliance": "Legal & Compliance",
    "Threat Intel": "Risk Management", 
    "Operations (General)": "Operations"
}

OPERATIONS_CONTROLS = [
    "A.8.1",  # User endpoint devices
    "A.8.7",  # Protection against malware 
    "A.8.10", # Information deletion
    "A.8.19", # Installation of software
]

def restore_processes():
    db = SessionLocal()
    try:
        print("Restoring Standard Processes via SubProcess Mapping...")
        
        existing_procs = {p.name: p for p in db.query(Process).all()}
        
        # 1. Create/Ensure Process and Default SubProcess
        proc_map = {} # name -> Process Obj
        subprocess_map = {} # ProcessName -> SubProcess Obj
        
        for p_name in STANDARD_PROCESSES:
            proc = existing_procs.get(p_name)
            if not proc:
                print(f"Creating Process: {p_name}")
                proc = Process(name=p_name, description=f"Standard {p_name} Process", framework_code="ISO27001")
                db.add(proc)
                db.commit() # Commit to get ID
                db.refresh(proc)
                existing_procs[p_name] = proc
            
            proc_map[p_name] = proc
            
            # Ensure at least one SubProcess exists for mapping
            # We'll use the same name "Standard {p_name}" or just "General"
            sp_name = f"{p_name} - General"
            sp = db.query(SubProcess).filter(SubProcess.process_id == proc.id, SubProcess.name == sp_name).first()
            if not sp:
                # Maybe there's another SP?
                if proc.sub_processes:
                    sp = proc.sub_processes[0]
                else:
                    print(f"Creating SubProcess for {p_name}")
                    sp = SubProcess(name=sp_name, description="Default subprocess", process_id=proc.id)
                    db.add(sp)
                    db.commit()
                    db.refresh(sp)
            
            subprocess_map[p_name] = sp

        # 2. Map Controls to SubProcesses
        controls = db.query(Control).all()
        
        for control in controls:
            target_process_name = None
            
            # A. Overrides
            if control.control_id in OPERATIONS_CONTROLS:
                target_process_name = "Operations"
            elif control.control_id == "A.8.12":
                target_process_name = "Cryptography" # User specific request
            elif control.control_id == "A.8.18":
                target_process_name = "Access Control (IAM)" # User specific request
            elif control.control_id == "A.8.24":
                target_process_name = "Cryptography"
            
            # B. Category Map
            if not target_process_name and control.category:
                target_process_name = CATEGORY_MAP.get(control.category)
            
            # C. Fallback
            if not target_process_name:
                if "backup" in control.title.lower():
                    target_process_name = "Operations"
                elif "log" in control.title.lower():
                    target_process_name = "Logging & Monitoring"

            # D. Apply to SubProcess
            if target_process_name and target_process_name in subprocess_map:
                sp = subprocess_map[target_process_name]
                
                if control not in sp.controls:
                    print(f"Mapping {control.control_id} to {target_process_name}")
                    sp.controls.append(control)

        # 3. Cleanup "Operations" if it exists and is invalid
        bad_op = db.query(Process).filter(Process.name == "Operations").first()
        if bad_op:
            print("Deleting monolithic 'Operations' process...")
            db.delete(bad_op)

        db.commit()
        print("Restoration Complete.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    restore_processes()
