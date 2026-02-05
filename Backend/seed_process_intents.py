
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
from app.services.policy_intents import POLICY_CONTROL_MAP

# Setup DB
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def seed_intent_processes():
    print("[-] Seeding Processes based on Policy Intents (The 688 Requirements)...")
    
    # 1. Clear existing mappings to avoid duplicates/confusion
    print("[-] Clearing existing process-control mappings...")
    db.execute(text("DELETE FROM process_control_mapping"))
    db.execute(text("DELETE FROM sub_processes"))
    db.execute(text("DELETE FROM processes"))
    db.commit()

    created_procs = 0
    mapped_count = 0
    
    # 2. Iterate Master Map
    for policy_name, control_ids in POLICY_CONTROL_MAP.items():
        # Create Process (The Policy Domain)
        # e.g. "Access Control Policy"
        proc = Process(name=policy_name, description=f"Controls and intents for {policy_name}")
        db.add(proc)
        db.commit()
        db.refresh(proc)
        created_procs += 1
        
        # Create SubProcess (The Grouping)
        # We could split this if we had finer granularity, but "Requirements" is a safe bucket
        sp = SubProcess(name="Policy Requirements", description="Mandatory controls for this policy", process_id=proc.id)
        db.add(sp)
        db.commit()
        db.refresh(sp)
        
        # Validation checks
        valid_controls = []
        for cid in control_ids:
            # Handle SOC 2 mapping? The DB might store them differently or they might be missing.
            # Our controls in DB are mostly ISO "A.5.1", "4.1" etc. or "CC1.1" etc.
            # Let's try exact match first
            c = db.query(Control).filter(Control.control_id == cid).first()
            
            # If not found, try stripping "ISO_" prefix if present in map but not DB
            if not c and cid.startswith("ISO_"):
                alt_cid = cid.replace("ISO_", "")
                c = db.query(Control).filter(Control.control_id == alt_cid).first()
            
            if c:
                valid_controls.append(c)
        
        # Bulk map
        if valid_controls:
            sp.controls.extend(valid_controls)
            mapped_count += len(valid_controls)
            
    db.commit()
    print(f"[SUCCESS] Created {created_procs} Processes based on Policy Intents.")
    print(f"[SUCCESS] Mapped {mapped_count} controls to these processes.")

if __name__ == "__main__":
    try:
        seed_intent_processes()
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()
