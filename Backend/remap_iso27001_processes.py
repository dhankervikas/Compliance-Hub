
from app.database import SessionLocal
from app.models.control import Control
from app.models.process import Process, SubProcess, process_control_mapping
from sqlalchemy import text

# Mapping Rules (Prefix -> Process Name)
# Based on ISO 27001:2013 structure which seems to match the control IDs (A.5.1 etc)
# Even though framework is labeled 2022, the IDs suggest 2013 or a hybrid.
MAPPING_RULES = {
    "A.5": "Governance & Policy",
    "A.6": "Governance & Policy", # Organization of InfoSec often goes here or separate
    "A.7": "HR Security",
    "A.8": "Asset Management",
    "A.9": "Access Control (IAM)",
    "A.10": "Cryptography",
    "A.11": "Physical Security",
    "A.12.1": "Operations (General)",
    "A.12.2": "Operations (General)",
    "A.12.3": "Backup Management", 
    "A.12.4": "Logging & Monitoring",
    "A.12.5": "Operations (General)",
    "A.12.6": "Vulnerability Management",
    "A.12.7": "Operations (General)",
    "A.13": "Network Security",
    "A.14": "SDLC (Development)",
    "A.15": "Supplier Mgmt",
    "A.16": "Incident & Resilience",
    "A.17": "Incident & Resilience", # BCPP
    "A.18": "Legal & Compliance",
    # Clauses
    "4.": "Governance & Policy",
    "5.": "Governance & Policy",
    "6.": "Risk Management",
    "7.": "Governance & Policy",
    "8.": "Operations",
    "9.": "Internal Audit", # Broad bucket
    "10.": "Improvement"
}

def remap():
    db = SessionLocal()
    try:
        print("Remapping ISO 27001 Controls...")

        # 1. Get Framework ID 13 Controls (The Active ISO 27001)
        ACTIVE_ISO_ID = 13
        controls = db.query(Control).filter(Control.framework_id == ACTIVE_ISO_ID).all()
        print(f"Found {len(controls)} controls for Framework ID {ACTIVE_ISO_ID}.")

        # 2. Get Processes and their First SubProcess
        processes = db.query(Process).filter(Process.framework_code == "ISO27001").all()
        proc_map = {} # Name -> SubProcess ID
        for p in processes:
            if p.sub_processes:
                proc_map[p.name] = p.sub_processes[0].id
            else:
                print(f"Warning: Process '{p.name}' has no subprocesses.")

        # 3. Clear Existing Mappings for these controls
        # We delete by control_id in bulk
        if controls:
            ids = [c.id for c in controls]
            # Batch delete
            # SQLite implies limit, but 123 is fine.
            id_list = ",".join(map(str, ids))
            db.execute(text(f"DELETE FROM process_control_mapping WHERE control_id IN ({id_list})"))
            print("Cleared old mappings.")

        # 4. Insert New Mappings
        mappings = []
        mapped_count = 0
        
        for c in controls:
            target_process = None
            # Find match by longest prefix match
            # e.g. A.12.1 matches A.12.1 before A.12 (if exists)
            # Actually simplest is startswith
            best_match = ""
            for prefix, p_name in MAPPING_RULES.items():
                if c.control_id.startswith(prefix):
                    if len(prefix) > len(best_match):
                        best_match = prefix
                        target_process = p_name
            
            if target_process and target_process in proc_map:
                sp_id = proc_map[target_process]
                mappings.append({"subprocess_id": sp_id, "control_id": c.id})
                mapped_count += 1
            else:
                # Fallback? Put in "Governance & Policy" or log
                # print(f"Unmapped: {c.control_id} - {c.title}")
                pass

        if mappings:
            db.execute(process_control_mapping.insert(), mappings)
            db.commit()
            print(f"Successfully remapped {mapped_count} controls.")
        else:
            print("No mappings generated.")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    remap()
