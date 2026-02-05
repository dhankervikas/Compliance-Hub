import sys
import os
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.control import Control

# Setup Path
sys.path.append(os.path.join(os.path.dirname(__file__), "."))

# Setup DB
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def check_duplicates():
    print("[-] Checking for duplicate control_ids...")
    
    # Find control_ids that appear more than once
    duplicates = db.query(Control.control_id, func.count(Control.control_id))\
        .group_by(Control.control_id)\
        .having(func.count(Control.control_id) > 1)\
        .all()
    
    if not duplicates:
        print("[OK] No duplicate control_ids found.")
    else:
        print(f"[WARN] Found {len(duplicates)} duplicate control_ids!")
        for code, count in duplicates:
            print(f" - {code}: {count} occurrences")
            
            # Detail view
            rows = db.query(Control).filter(Control.control_id == code).all()
            for r in rows:
                print(f"   > ID: {r.id} | Proc: {r.process_name} | Domain: {r.domain}")

if __name__ == "__main__":
    check_duplicates()
