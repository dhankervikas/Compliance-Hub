import json
import os
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

KEYWORDS_FILE = os.path.join(os.path.dirname(__file__), "app", "services", "process_keywords.json")

def load_keywords():
    with open(KEYWORDS_FILE, 'r') as f:
        return json.load(f)

def bulk_auto_categorize():
    print("[-] Starting Bulk Auto-Categorization...")
    keyword_map = load_keywords()
    
    # Get All Controls
    controls = db.query(Control).filter(Control.framework_id == 1).all() # Targeting ISO 27001 primarily
    processes = db.query(Process).all()
    process_lookup = {p.name: p for p in processes}
    
    count = 0
    updated = 0
    
    for c in controls:
        count += 1
        # Check if already categorized
        if c.sub_processes:
            continue # Skip if already mapped
            
        # Determine Target Category
        target_process_name = "Governance & Policy" # Default Safety Net
        
        # 1. SPECIAL CASE: Clause 6.3
        if c.control_id == "6.3":
            target_process_name = "Governance & Policy"
            print(f"[Override] Clause 6.3 -> Governance & Policy")
            
        else:
            # 2. KEYWORD MATCHING
            text = (c.title + " " + (c.description or "")).lower()
            found = False
            for process_name, keywords in keyword_map.items():
                if any(k in text for k in keywords):
                    target_process_name = process_name
                    found = True
                    break
            
            if not found:
                print(f"[Default] '{c.title}' -> Governance & Policy")
                
        # Link to Process
        target_process = process_lookup.get(target_process_name)
        if not target_process:
            print(f"Error: Process '{target_process_name}' not found!")
            continue
            
        sp_name = f"Intent: {c.title}"[:100]
        sp = db.query(SubProcess).filter(SubProcess.process_id == target_process.id, SubProcess.name == sp_name).first()
        
        if not sp:
            sp = SubProcess(name=sp_name, process_id=target_process.id)
            db.add(sp)
            db.flush()
            
        c.sub_processes.append(sp)
        updated += 1
        print(f"Mapped {c.control_id} -> {target_process_name}")
        
    db.commit()
    print(f"\n[+] Processing Complete. {updated} controls categorized.")

if __name__ == "__main__":
    bulk_auto_categorize()
