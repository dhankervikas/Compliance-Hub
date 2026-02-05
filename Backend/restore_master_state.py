import sys
import os
import shutil
import csv
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "."))

from app.database import Base
from app.config import settings
from app.models.process import Process, SubProcess, process_control_mapping
from app.models.control import Control
from app.models.framework import Framework
from app.models.tenant import Tenant

# Constants
MASTER_FILE = r"C:\Projects\Compliance_Product\Backend\MASTER_ISO27001_INTENTS.csv"
BACKUP_DB = r"C:\Projects\Compliance_Product\Backend\compliance_backup_restore.db"
ISO_FRAMEWORK_CODE = "ISO27001"

# 21 Canonical Processes (Hardcoded Source of Truth)
CANONICAL_PROCESSES = [
    "Governance & Policy",
    "HR Security",
    "Asset Management",
    "Access Control (IAM)",
    "Physical Security",
    "Operations (General)",
    "Configuration Management",
    "Cryptography",
    "Logging & Monitoring",
    "Clock Synchronization",
    "Vulnerability Management",
    "Capacity Management",
    "Backup Management",
    "Network Security",
    "SDLC (Development)",
    "Supplier Mgmt",
    "Incident & Resilience",
    "Threat Intel",
    "Legal & Compliance",
    "Risk Management",
    "Internal Audit",
    "Management Review",
    "Improvement"
]

def restore_master_state():
    print(f"[-] Starting RESTORE_MASTER_STATE...")
    
    # 1. Connect DB
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 2. Safety Backup (Copy sqlite file or dump)
        # Assuming SQLite for local dev
        if "sqlite" in settings.DATABASE_URL:
             db_path = settings.DATABASE_URL.replace("sqlite:///", "")
             if os.path.exists(db_path):
                 shutil.copy(db_path, BACKUP_DB)
                 print(f"[+] Backup created at {BACKUP_DB}")
        
        # 3. Resolve Tenant & Framework
        # We need to clean up data for ALL tenants or specific?
        # User said "Restore Processes", usually implies global or current tenant.
        # Let's target the DEFAULT usage for now (single tenant mode effectively).
        
        iso_fw = db.query(Framework).filter(Framework.code == ISO_FRAMEWORK_CODE).first()
        if not iso_fw:
            print("[-] ISO27001 Framework not found. Creating...")
            iso_fw = Framework(code=ISO_FRAMEWORK_CODE, name="ISO 27001:2022", description="Information Security", is_active=True)
            db.add(iso_fw)
            db.commit()
            db.refresh(iso_fw)
            
        print(f"[-] Target Framework ID: {iso_fw.id}")
        
        # 4. PURGE DATA (Destructive)
        print("[-] PURGING Existing Process/Control Data for ISO 27001...")
        
        # Delete Mappings first
        db.execute(text("DELETE FROM process_control_mapping"))
        
        # Delete SubProcesses for this framework's processes
        # Simple approach: Delete ALL processes linked to ISO or created by seeding
        # We'll filter Process by framework_code
        procs = db.query(Process).filter(Process.framework_code == ISO_FRAMEWORK_CODE).all()
        proc_ids = [p.id for p in procs]
        if proc_ids:
            db.execute(text(f"DELETE FROM sub_processes WHERE process_id IN ({','.join(map(str, proc_ids))})"))
            db.execute(text(f"DELETE FROM processes WHERE id IN ({','.join(map(str, proc_ids))})"))
            
        # Delete Controls for this Framework
        db.execute(text(f"DELETE FROM controls WHERE framework_id = {iso_fw.id}"))
        
        db.commit()
        print("[+] Purge Complete.")
        
        # 5. Seed Canonical Processes
        print("[-] Seeding 21 Canonical Processes...")
        proc_map = {} # Name -> DB Object
        for p_name in CANONICAL_PROCESSES:
            p = Process(
                name=p_name, 
                description=f"Core Process: {p_name}",
                framework_code=ISO_FRAMEWORK_CODE
            )
            db.add(p)
            db.commit() # Commit each to get ID
            db.refresh(p)
            proc_map[p_name] = p
            
        print(f"[+] Created {len(proc_map)} Processes.")
        
        # 6. Ingest Master File
        print(f"[-] Ingesting Master File: {MASTER_FILE}")
        df = pd.read_csv(MASTER_FILE)
        
        # Deduplication Set
        seen_intents = set()
        
        # Prepare Batch Insert
        controls_to_add = []
        mappings_to_add = []
        
        # Fix 0% Dashboard: Calculate Stats
        stats = {"implemented": 0, "in_progress": 0, "not_started": 0, "total": 0}
        
        for index, row in df.iterrows():
            intent_id = str(row.get('Intent_id', index)) # Fallback if missing
            
            # Constraints: Deduplication
            if intent_id in seen_intents:
                continue
            seen_intents.add(intent_id)
            
            # Constraints: Process Binding
            p_name = row.get('Process', 'Uncategorized')
            parent_proc = proc_map.get(p_name)
            
            # Fallback to Uncategorized if not in 21 list (Strict "No Guessing")
            if not parent_proc:
                # Create Uncategorized bucket if not exists?
                # or just skip? User said "Put it in an 'Uncategorized' folder"
                uncat_proc = proc_map.get("Uncategorized")
                if not uncat_proc:
                     uncat_proc = Process(name="Uncategorized", description="Unmapped items", framework_code=ISO_FRAMEWORK_CODE)
                     db.add(uncat_proc)
                     db.commit()
                     db.refresh(uncat_proc)
                     proc_map["Uncategorized"] = uncat_proc
                parent_proc = uncat_proc
            
            # Create SubProcess (One per Intent/Control? Or Group?)
            # Usually SubProcess = Policy/Control Group.
            # For simplicity in this flat list, let's map Control directly via a "General" subprocess for each Process?
            # Or make a subgroup for the control?
            # Let's Check: User said "If an intent is in that file, it MUST appear under its assigned process."
            # Creating a SubProcess called 'Controls' for each Process is cleanest.
            if not getattr(parent_proc, 'default_subprocess_id', None):
                 # Check DB
                 sp = db.query(SubProcess).filter(SubProcess.process_id == parent_proc.id, SubProcess.name == "Controls").first()
                 if not sp:
                     sp = SubProcess(name="Controls", description="Mapped Controls", process_id=parent_proc.id)
                     db.add(sp)
                     db.commit()
                     db.refresh(sp)
                 parent_proc.default_subprocess_id = sp.id
                 
            # Create Control
            # "Action-Oriented Translation": Use Action_Title
            title = row.get('Action_Title', f"Implement {row.get('Clause_or_control')}")
            
            # Use Intent_ID as the Unique Control ID (User Constraint)
            # Original Clause is preserved in description or could be appended
            control_id = intent_id # e.g. INT-04-01
            
            # Fallback if Intent ID is missing
            if not control_id or control_id == "nan":
                control_id = f"UNK-{index}"
            
            # Status Logic (Vanta-Style)
            raw_status = row.get('compliance_status', 'Not Started')
            if raw_status == 'Compliant':
                status = 'implemented'
            else:
                # Default to 'not_started' (4-dot indicator empty state)
                status = 'not_started'
                
            c = Control(
                control_id=control_id,
                title=title,
                description=str(row.get('Intent_statement', '')),
                status=status,
                framework_id=iso_fw.id,
                category=p_name, # Mapped Process
                tenant_id="default_tenant"
            )
            db.add(c)
            db.commit() # Need ID for mapping
            db.refresh(c)
            
            # Mapping
            mappings_to_add.append({"subprocess_id": parent_proc.default_subprocess_id, "control_id": c.id})
            
            # Stats
            stats['total'] += 1
            if status in stats:
                stats[status] += 1
                
        # Bulk Insert Mappings
        if mappings_to_add:
            db.execute(process_control_mapping.insert(), mappings_to_add)
            db.commit()
            
        print(f"[+] Ingested {len(seen_intents)} Unique Intents.")
        
        # 7. Sync Dashboard (Update TenantFramework Progress)
        print("[-] Syncing Dashboard Progress...")
        # Percentage
        pct = 0
        if stats['total'] > 0:
             # Logic: (Implemented * 1 + InProgress * 0.5) / Total ? Or just Implemented?
             # Simple: Implemented / Total
             pct = int((stats['implemented'] / stats['total']) * 100)
             
        # Update DB
        from app.models.tenant_framework import TenantFramework
        tfs = db.query(TenantFramework).filter(TenantFramework.framework_id == iso_fw.id).all()
        for tf in tfs:
            tf.progress = pct
            tf.status = "active"
            db.add(tf)
            
        db.commit()
        print(f"[+] Dashboard Synced: {pct}% based on {stats}")
        
    except Exception as e:
        print(f"[!] Error: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    restore_master_state()
