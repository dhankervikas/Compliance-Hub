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

def fix_uncategorized():
    print("[-] Fixing Uncategorized Controls...")
    
    # Get ISO Framework
    iso = db.query(Framework).filter(Framework.code.like("ISO27001%")).first()
    if not iso:
        print("ISO Framework not found")
        return

    # Mappings for the 23 detected uncategorized controls
    # Based on ISO 27001:2022 Structure -> Canonical Process
    MANUAL_MAPPINGS = {
        "4.4": "Governance & Policy",
        "6.1.1": "Risk Management",
        "6.3": "Change Management", # Or "Governance & Policy" / "Configuration Management"
        "7.1": "Governance & Policy",
        "7.4": "Governance & Policy", # Communication
        "7.5.1": "Governance & Policy", # Documented Info
        "7.5.2": "Governance & Policy",
        "7.5.3": "Governance & Policy",
        "8.1": "Operations (General)",
        "8.2": "Risk Management",
        "8.3": "Risk Management",
        "9.1": "Performance Evaluation",
        "9.2.1": "Performance Evaluation", # Internal Audit
        "9.2.2": "Performance Evaluation",
        "9.3.1": "Performance Evaluation", # Mgmt Review
        "9.3.2": "Performance Evaluation",
        "9.3.3": "Performance Evaluation",
        "10.1": "Improvement",
        "10.2": "Improvement",
        "A.7.5": "Physical Security", # Protecting against physical threats
        # Add any others that might appear
    }

    # Fetch and Update
    controls = db.query(Control).filter(
        Control.framework_id == iso.id
    ).all()
    
    count = 0
    
    # Pre-fetch processes to link
    processes = db.query(Process).all()
    process_map = {p.name: p for p in processes}
    
    # Ensure all target processes exist, fallback to "Governance & Policy"
    default_process = process_map.get("Governance & Policy")

    for c in controls:
        # Check if needs fixing (no sub_processes mapped)
        if not c.sub_processes:
            target_process_name = MANUAL_MAPPINGS.get(c.control_id)
            
            if not target_process_name:
                # Fallback logic if not in manual list
                if c.control_id.startswith("5"): target_process_name = "Governance & Policy"
                elif c.control_id.startswith("6"): target_process_name = "Risk Management"
                elif c.control_id.startswith("7"): target_process_name = "Governance & Policy" # Support
                elif c.control_id.startswith("8"): target_process_name = "Operations (General)"
                elif c.control_id.startswith("9"): target_process_name = "Performance Evaluation"
                elif c.control_id.startswith("10"): target_process_name = "Improvement"
                elif c.control_id.startswith("A.5"): target_process_name = "Governance & Policy"
                elif c.control_id.startswith("A.6"): target_process_name = "HR Security"
                elif c.control_id.startswith("A.7"): target_process_name = "Physical Security"
                elif c.control_id.startswith("A.8"): target_process_name = "Operations (General)"
                else: target_process_name = "Governance & Policy" # Ultimate Fallback
            
            # Find/Create SubProcess mapping
            target_process = process_map.get(target_process_name)
            if not target_process:
                print(f"Warning: Target process {target_process_name} not found in DB")
                continue
                
            # Create SubProcess Link (Intent)
            # We treat the Control Title as the 'Intent' or generic SubProcess name if one doesn't exist
            sp_name = f"Intent: {c.title}"[:100] 
            
            # Check if SP exists
            sp = db.query(SubProcess).filter(
                SubProcess.process_id == target_process.id,
                SubProcess.name == sp_name
            ).first()
            
            if not sp:
                sp = SubProcess(name=sp_name, process_id=target_process.id)
                db.add(sp)
                db.flush()
            
            # Link Control to SubProcess
            if sp not in c.sub_processes:
                c.sub_processes.append(sp)
                count += 1
                print(f"Mapped {c.control_id} -> {target_process_name}")

    db.commit()
    print(f"\n[+] Successfully mapped {count} previously uncategorized controls.")

if __name__ == "__main__":
    fix_uncategorized()
