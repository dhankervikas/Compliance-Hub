from app.database import SessionLocal, engine, Base
from app.models.universal_intent import UniversalIntent, IntentStatus
from app.models.intent_framework_crosswalk import IntentFrameworkCrosswalk
from app.models.framework import Framework
from app.models.person import Person
from app.models.control import Control
from app.models.process import Process, SubProcess
from sqlalchemy.orm import Session
from sqlalchemy import text
import csv
import os

# Ensure tables exist
Base.metadata.create_all(bind=engine)

# STRICT 21 CANONICAL PROCESSES
CANONICAL_PROCESSES = [
    "Governance & Policy",
    "HR Security",
    "Asset Management",
    "Access Control (IAM)",
    "Physical Security",
    "Operations", # RENAMED from Operations (General)
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
    "Improvement",
    "Internal Audit",
    "Management Review"
]

# Mapping Rules (Prefix -> Process Name)
MAPPING_RULES = {
    # --- ISO 27001:2022 Mappings (User Overrides Applied) ---
    
    # A.5: Organizational
    "A.5.1": "Governance & Policy", "A.5.2": "Governance & Policy", "A.5.3": "Governance & Policy",
    "A.5.4": "Governance & Policy", "A.5.5": "Governance & Policy", "A.5.6": "Governance & Policy",
    "A.5.7": "Threat Intel",
    "A.5.8": "Governance & Policy",
    "A.5.9": "Asset Management", "A.5.10": "Asset Management", 
    "A.5.11": "Asset Management", 
    "A.5.12": "Asset Management", 
    "A.5.13": "Asset Management", 
    "A.5.14": "Network Security", # MOVED from Governance to Network
    "A.5.15": "Access Control (IAM)", "A.5.16": "Access Control (IAM)", "A.5.17": "Access Control (IAM)", "A.5.18": "Access Control (IAM)",
    "A.5.19": "Supplier Mgmt", "A.5.20": "Supplier Mgmt", "A.5.21": "Supplier Mgmt", "A.5.22": "Supplier Mgmt", "A.5.23": "Supplier Mgmt",
    "A.5.24": "Incident & Resilience", "A.5.25": "Incident & Resilience", "A.5.26": "Incident & Resilience", 
    "A.5.27": "Incident & Resilience", "A.5.28": "Incident & Resilience",
    "A.5.29": "Incident & Resilience", "A.5.30": "Incident & Resilience", 
    "A.5.31": "Legal & Compliance", "A.5.32": "Legal & Compliance", "A.5.33": "Legal & Compliance", 
    "A.5.34": "Legal & Compliance", "A.5.35": "Internal Audit", "A.5.36": "Legal & Compliance", 
    "A.5.37": "Governance & Policy", # MOVED from Legal (Assumed 'Clause A.37' means A.5.37)

    # A.6: People
    "A.6": "HR Security",

    # A.7: Physical
    "A.7": "Physical Security",
    "A.7.10": "Asset Management", # MOVED to Asset
    "A.7.14": "Asset Management", # MOVED to Asset

    # A.8: Technological
    "A.8.1": "Operations", # MOVED from Asset to Operations
    "A.8.2": "Access Control (IAM)", "A.8.3": "Access Control (IAM)", "A.8.4": "Access Control (IAM)", "A.8.5": "Access Control (IAM)",
    "A.8.6": "Capacity Management",
    "A.8.7": "Operations", # Renamed
    "A.8.8": "Vulnerability Management",
    "A.8.9": "Configuration Management",
    "A.8.10": "Operations", # MOVED from Asset to Operations
    "A.8.11": "Cryptography", # MOVED from Asset to Crypto
    "A.8.12": "Operations", # MOVED from Asset to Operations
    "A.8.13": "Backup Management",
    "A.8.14": "Incident & Resilience", 
    "A.8.15": "Logging & Monitoring", "A.8.16": "Logging & Monitoring", "A.8.17": "Clock Synchronization",
    "A.8.18": "Access Control (IAM)", 
    "A.8.19": "Operations", 
    "A.8.20": "Network Security", "A.8.21": "Network Security", "A.8.22": "Network Security", "A.8.23": "Network Security",
    "A.8.24": "Cryptography",
    "A.8.25": "SDLC (Development)", "A.8.26": "SDLC (Development)", "A.8.27": "SDLC (Development)", 
    "A.8.28": "SDLC (Development)", "A.8.29": "SDLC (Development)", "A.8.30": "SDLC (Development)",
    "A.8.31": "SDLC (Development)", "A.8.32": "SDLC (Development)", "A.8.33": "SDLC (Development)",
    "A.8.34": "Legal & Compliance", 

    # Legacy / Clauses
    "9.1": "Logging & Monitoring", # ADDED
    "9.2": "Internal Audit",
    "9.3": "Management Review",
    "10.": "Improvement",
    
    # Overrides
    "A.9.2": "Internal Audit", 
    "A.9.3": "Management Review",
    "8.": "Operations" # Update legacy fallback
}

def get_process_for_control(control_id):
    """Determine Canonical Process based on Control ID Prefix"""
    best_match = None
    best_len = 0
    
    # Normalize ID for matching (Ensure starts with A. if ISO)
    # But checking raw startsWith is safer for the map keys
    
    for prefix, p_name in MAPPING_RULES.items():
        if control_id.startswith(prefix):
            if len(prefix) > best_len:
                best_match = p_name
                best_len = len(prefix)
    
    return best_match or "Governance & Policy" # Default fallback

def seed_master_intents(db: Session):
    print("--- SEEDING MASTER INTENTS (STRICT 21 PROCESSES) ---")
    
    # Resolve CSV Path relative to script location
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "MASTER_ISO27001_INTENTS.csv")
    
    if not os.path.exists(csv_path):
        print(f"ERROR: CSV file not found at {csv_path}")
        return

    # 1. SETUP PROCESSES
    print("[-] Ensuring 21 Canonical Processes exist...")
    process_map = {} # Name -> Process Obj
    
    # Check existing or create
    existing = db.query(Process).filter(Process.framework_code == "ISO27001").all()
    existing_map = {p.name: p for p in existing}
    
    for p_name in CANONICAL_PROCESSES:
        if p_name in existing_map:
            process_map[p_name] = existing_map[p_name]
        else:
            new_proc = Process(
                name=p_name,
                description=f"Controls related to {p_name}",
                framework_code="ISO27001"
            )
            db.add(new_proc)
            db.commit() # Commit to get ID
            db.refresh(new_proc)
            process_map[p_name] = new_proc
            
    # Clean up any processes NOT in the list? 
    # Optional: might delete user data if we are too aggressive. 
    # For now, just focus on populating these 21.

    # 2. READ CSV
    rows = []
    encodings = ['utf-8-sig', 'utf-8', 'cp1252', 'latin1']
    for enc in encodings:
        try:
            with open(csv_path, mode='r', encoding=enc) as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            break
        except UnicodeDecodeError: continue
            
    if not rows:
        print("Failed to read CSV.")
        return

    print(f"[-] Processing {len(rows)} intents...")
    
    seen_intents = set()
    mapped_count = 0
    
    for row in rows:
        intent_id = row.get('Intent_id')
        statement = row.get('Intent_statement')
        clause = row.get('Clause_or_control', '').strip()
        standard = row.get('Standard')
        
        if not intent_id or not statement:
            continue
            
        # NORMALIZE CONTROL REF
        control_ref = clause
        # Ensure A. prefix if missing for 5.x - 8.x (ISO 2022 usually)
        if standard == 'ISO27001_2022' and clause and clause[0].isdigit():
             if clause.startswith(('5.', '6.', '7.', '8.')):
                control_ref = f"A.{clause}"
        
        # DETERMINE PROCESS
        process_name = get_process_for_control(control_ref)
        if process_name not in process_map:
            # Fallback for unmatched prefixes
             process_name = "Governance & Policy"

        # 3. UPSERT UNIVERSAL INTENT
        # Deduplication: If we already processed this Intent ID in this run, skip re-updating meta
        # But we might need to check DB if it existed from before
        
        ui = db.query(UniversalIntent).filter(UniversalIntent.intent_id == intent_id).first()
        if not ui:
            ui = UniversalIntent(
                intent_id=intent_id,
                description=statement,
                category=process_name, 
                status=IntentStatus.PENDING
            )
            db.add(ui)
            db.commit()
            db.refresh(ui)
            seen_intents.add(intent_id)
        else:
            # Update Category only if not set or forcing update
            # Enforce the new mapping
            if ui.category != process_name:
                ui.category = process_name
                db.add(ui)
                db.commit()
        
        # 4. CROSSWALK (Link Intent -> ControlRef)
        cw = db.query(IntentFrameworkCrosswalk).filter(
            IntentFrameworkCrosswalk.intent_id == ui.id,
            IntentFrameworkCrosswalk.framework_id == "ISO27001",
            IntentFrameworkCrosswalk.control_reference == control_ref
        ).first()
        
        if not cw:
            cw = IntentFrameworkCrosswalk(
                intent_id=ui.id,
                framework_id="ISO27001",
                control_reference=control_ref
            )
            db.add(cw)
            db.commit()
            
        # 5. SYNC TO SIDEBAR (SubProcess)
        # Link the actual Control object to the Process -> SubProcess("Controls")
        
        target_process = process_map[process_name]
        
        # Ensure "Mapped Controls" SubProcess
        subprocess_name = "Mapped Controls"
        target_subprocess = None
        
        # ... (SubProcess finding logic inferred to be here or next)
        
        # UPDATE CONTROL REQUIREMENTS (EVIDENCE CHECKLIST)
        # Parse Evidence_examples column
        evidence_str = row.get('Evidence_examples', '')
        requirements_list = []
        if evidence_str and evidence_str.lower() != 'nan':
            # Split by comma or semicolon
            items = [x.strip() for x in evidence_str.replace(';', ',').split(',')]
            for item in items:
                if item:
                    requirements_list.append({
                        "name": item,
                        "desc": "Required per Master Intent Library",
                        "type": "Artifact" # Default type
                    })
        
        import json
        
        # Find the Control Object to update
        # We need to find the control that matches this framework & control_id
        control_obj = db.query(Control).filter(
            Control.framework_id == 1, # ISO27001
            Control.control_id == control_ref
        ).first()
        
        if control_obj:
            # Map SubProcess
            # (Logic to map subprocess is handled in loop below or elsewhere in original script, 
            #  but we must update the requirements here)
            if requirements_list:
                control_obj.ai_requirements_json = json.dumps(requirements_list)
                db.add(control_obj)
                db.commit()
        for sp in target_process.sub_processes:
            if sp.name == subprocess_name:
                target_subprocess = sp
                break
        
        if not target_subprocess:
            target_subprocess = SubProcess(
                name=subprocess_name,
                description="Controls linked to intents",
                process_id=target_process.id
            )
            db.add(target_subprocess)
            db.commit()
            db.refresh(target_subprocess)
            
        # Find Control Object
        # Matches control_id = control_ref
        control_obj = db.query(Control).filter(
            Control.control_id == control_ref,
            Control.framework_id == 1 # Safe-ish assumption for main ISO framework
        ).first()
        
        if control_obj:
            # ENFORCE 1:1 MAPPING (Strict Parent)
            # Replace ALL subprocess definitions with this SINGLE one
            # Using SQLAlchemy Relationship setter
            control_obj.sub_processes = [target_subprocess]
            
            # Ensure Control Category matches
            control_obj.category = process_name
            
            # ACTIONABLE TITLE UPGRADE
            action_title = row.get('Action_Title')
            if action_title:
                control_obj.title = action_title
                
            db.add(control_obj)
            db.commit()
            mapped_count += 1

    print(f"[SUCCESS] Processed {len(seen_intents)} Unique Intents. Mapped {mapped_count} Controls to 21 Processes.")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_master_intents(db)
    finally:
        db.close()
