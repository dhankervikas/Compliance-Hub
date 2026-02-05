
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "."))

from app.database import Base
from app.config import settings
from app.models.process import Process, SubProcess
from app.models.control import Control

# Setup DB
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def seed_processes():
    print("[-] Re-Seeding Processes and Control Mappings...")
    
    # 1. Define Standard Processes (The "Buckets")
    # Map Category -> Process Name
    category_map = {
        "Governance": "Governance & Policy",
        "Legal & Compliance": "Governance & Policy", # Compliance often grouped with Gov
        "Improvement": "Governance & Policy",
        "Performance Evaluation": "Governance & Policy",
        
        "Risk Management": "Risk Management",
        
        "HR Security": "Human Resources",
        
        "Asset Management": "Asset Management",
        
        "Access Control (IAM)": "Access Control",
        
        "Cryptography": "Cryptography",
        
        "Physical Security": "Physical & Environmental Security",
        
        "Operations": "Operations Security",
        "Backup Management": "Operations Security",
        "Capacity Management": "Operations Security",
        "Clock Synchronization": "Operations Security",
        "Threat Intel": "Operations Security",
        "Vulnerability Management": "Operations Security", # Or distinct?
        "Configuration Management": "Operations Security",
        "Logging & Monitoring": "Operations Security",
        
        "Network Security": "Communications Security",
        
        "Supplier Mgmt": "Supplier Relationships",
        
        "Incident & Resilience": "Incident Management",
        
        "SDLC (Development)": "System Development & Maintenance"
    }
    
    # Create Processes & Default SubProcess if not exist
    process_cache = {} # Name -> SubProcess Object
    
    created_procs = 0
    
    unique_processes = sorted(list(set(category_map.values())))
    
    # Delete existing mappings to ensure clean slate? 
    # Or just append? Safe to clear if we want a strict reset.
    # Let's clear mappings first to avoid duplicates if validation missing
    print("[-] Clearing existing process-control mappings...")
    db.execute(text("DELETE FROM process_control_mapping"))
    db.commit()

    for proc_name in unique_processes:
        # Get or Create Process
        proc = db.query(Process).filter(Process.name == proc_name).first()
        if not proc:
            proc = Process(name=proc_name, description=f"Standard process for {proc_name}")
            db.add(proc)
            db.commit()
            db.refresh(proc)
            created_procs += 1
            
        # Get or Create Standard SubProcess (we'll just map everything to "General" or "Standard Controls" for now to keep it simple)
        # Ideally, we'd map "Governance" -> "Policies", "Legal" -> "Compliance Requirements", etc.
        # But for now, flattening per Process is a good first step.
        sp_name = "Standard Controls"
        sp = db.query(SubProcess).filter(SubProcess.process_id == proc.id, SubProcess.name == sp_name).first()
        if not sp:
            sp = SubProcess(name=sp_name, description="Main controls", process_id=proc.id)
            db.add(sp)
            db.commit()
            db.refresh(sp)
        
        process_cache[proc_name] = sp
        
    print(f"[+] Verified {len(unique_processes)} Standard Processes (Created {created_procs} new).")
    
    # 2. Map Controls (The "Contents")
    # Iterate ALL controls
    controls = db.query(Control).all()
    print(f"[-] Mapping {len(controls)} controls to processes...")
    
    count = 0
    for control in controls:
        cat = control.category
        if not cat:
            # Fallback or Skip
            continue
            
        target_process_name = category_map.get(cat)
        if not target_process_name:
            # Maybe map to "General" or "Other"?
            # Let's try to infer or skip
            # print(f"Warning: Unmapped category '{cat}' for control {control.control_id}")
            continue
            
        target_sp = process_cache.get(target_process_name)
        if target_sp:
            target_sp.controls.append(control)
            count += 1
            
    db.commit()
    print(f"[SUCCESS] Mapped {count} controls to processes.")

if __name__ == "__main__":
    try:
        seed_processes()
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()
