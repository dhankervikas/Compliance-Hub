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

# Constants
MASTER_FILE = r"C:\Projects\Compliance_Product\Backend\MASTER_ISO27001_INTENTS.csv"

def update_titles():
    print(f"[-] Starting UPDATE_CONTROL_TITLES...")
    
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 1. Ingest Master File
        print(f"[-] Reading Master File: {MASTER_FILE}")
        df = pd.read_csv(MASTER_FILE)
        
        count = 0
        
        # 2. Iterate and Update
        for index, row in df.iterrows():
            intent_id = str(row.get('Intent_id', index))
            
            # Find Control
            # We need to update globally (all tenants).
            controls = db.query(Control).filter(Control.control_id == intent_id).all()
            
            if not controls:
                continue
                
            long_sentence = str(row.get('Intent_statement', ''))
            standard_name = str(row.get('Action_Title', ''))
            
            # Fallback if empty
            if not long_sentence or long_sentence == 'nan':
                 long_sentence = standard_name
            
            for c in controls:
                # SWAP LOGIC:
                # Title = Long Sentence
                # Description = Standard Name
                
                c.title = long_sentence
                c.description = standard_name
                db.add(c)
                count += 1
            
        db.commit()
        print(f"[+] SUCCESS: Updated titles for {count} control records.")
        
    except Exception as e:
        print(f"[!] Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_titles()
