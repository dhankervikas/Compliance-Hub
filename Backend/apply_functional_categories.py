import json
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from app.database import Base
from app.config import settings
from app.models.control import Control
from app.models.process import Process, SubProcess
from app.models.framework import Framework

# Setup DB
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

MAPPING_FILE = os.path.join(os.path.dirname(__file__), "app", "services", "functional_mapping.json")

def load_mapping():
    with open(MAPPING_FILE, 'r') as f:
        return json.load(f)

def apply_categories():
    print("[-] Applying Functional Categories...")
    mapping = load_mapping()
    
    controls = db.query(Control).options(
        joinedload(Control.sub_processes).joinedload(SubProcess.process)
    ).all()
    
    count = 0
    
    for c in controls:
        new_category = "Governance" # Default
        
        # Rule 1: ISO Clauses 4-10 -> Governance
        # (This overrides process mapping if needed, but usually aligns)
        is_clause = False
        if "ISO27001" in (c.framework.code or ""):
             # Check ID
             cid = c.control_id
             if cid and (cid.startswith("4") or cid.startswith("5") or cid.startswith("6") or cid.startswith("7") or cid.startswith("8") or cid.startswith("9") or cid.startswith("10")):
                if not cid.startswith("A."):
                    new_category = "Governance"
                    is_clause = True

        # Rule 2: Process Mapping (if not forced by clause logic, or to refine)
        # Actually user said "Clause 6.3 check" -> It's a clause, so Rule 1 covers it.
        # But let's check process mapping for the rest.
        
        if not is_clause:
            p_name = c.process_name # Property
            if p_name:
                # Normalize legacy names?
                # The property returns the mapped process name.
                mapped_cat = mapping.get(p_name)
                if mapped_cat:
                    new_category = mapped_cat
                else:
                    print(f"Warning: Process '{p_name}' not in mapping. Defaulting to Governance.")
            else:
                # If no process, it's truly uncategorized. Default to Governance.
                pass
        
        # Update DB
        if c.category != new_category:
            c.category = new_category
            count += 1
            # print(f"Updated {c.control_id}: {c.category} -> {new_category}")
            
    db.commit()
    print(f"[+] Successfully updated {count} controls to Functional Categories.")

if __name__ == "__main__":
    apply_categories()
