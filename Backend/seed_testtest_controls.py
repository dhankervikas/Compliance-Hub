import sys
import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "."))

from app.database import Base
from app.config import settings
from app.models.control import Control
from app.models.framework import Framework

# Constants
MASTER_FILE = r"C:\Projects\Compliance_Product\Backend\MASTER_ISO27001_INTENTS.csv"
ISO_FRAMEWORK_CODE = "ISO27001"
TARGET_TENANT_ID = "a61624c9-b0d9-4125-9bd5-edf7af8fb78e"

def seed_testtest():
    print(f"[-] Starting SEED_TESTTEST_CONTROLS for {TARGET_TENANT_ID}...")
    
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 1. Get Framework ID
        iso_fw = db.query(Framework).filter(Framework.code == ISO_FRAMEWORK_CODE).first()
        if not iso_fw:
             print("[!] ISO27001 Framework missing! Run restore_master_state.py first.")
             return
             
        # 2. Clear Existing Controls for this Tenant (Safety)
        print("[-] Clearing existing controls for this tenant...")
        # Use simple delete
        deleted = db.query(Control).filter(Control.tenant_id == TARGET_TENANT_ID, Control.framework_id == iso_fw.id).delete()
        db.commit()
        print(f"[+] Deleted {deleted} existing controls.")
        
        # 3. Ingest Master File
        print(f"[-] Ingesting Master File: {MASTER_FILE}")
        df = pd.read_csv(MASTER_FILE)
        
        seen_intents = set()
        count = 0
        
        for index, row in df.iterrows():
            intent_id = str(row.get('Intent_id', index))
            
            # Deduplication
            if intent_id in seen_intents:
                continue
            seen_intents.add(intent_id)
            
            p_name = row.get('Process', 'Uncategorized')
            title = row.get('Action_Title', f"Implement {row.get('Clause_or_control')}")
            control_id = intent_id
            
            # Status Logic
            raw_status = row.get('compliance_status', 'Not Started')
            if raw_status == 'Compliant':
                status = 'implemented'
            else:
                status = 'not_started'
                
            c = Control(
                control_id=control_id,
                title=title,
                description=str(row.get('Intent_statement', '')),
                status=status,
                framework_id=iso_fw.id,
                category=p_name,
                tenant_id=TARGET_TENANT_ID
            )
            db.add(c)
            count += 1
            
        db.commit()
        print(f"[+] SUCCESS: Seeded {count} controls for TestTest.")
        
    except Exception as e:
        print(f"[!] Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_testtest()
