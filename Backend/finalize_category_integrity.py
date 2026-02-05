from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.config import settings
from app.models.control import Control

# Setup DB
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def finalize_integrity():
    print("[-] Finalizing Category Data Integrity...")
    
    # 1. Fetch controls with NULL or Empty Category
    controls = db.query(Control).filter(
        (Control.category == None) | (Control.category == "")
    ).all()
    
    count = 0
    for c in controls:
        c.category = "Governance"
        count += 1
        
    db.commit()
    print(f"[+] Fixed {count} controls with missing category (Defaulted to Governance).")
    
    # 2. Verify Clause 6.3 specifically
    c63 = db.query(Control).filter(Control.control_id == "6.3").first()
    if c63:
        if c63.category != "Governance":
            c63.category = "Governance"
            db.commit()
            print("[+] Explicitly set Clause 6.3 to Governance.")
        # Also check Process Mapping if using that for Header
        # The frontend uses process_name. Let's ensure it maps to Governance & Policy.
        # We previously did this via sub_process link.
        # This script focuses on the Control.category column (The Badge).

if __name__ == "__main__":
    finalize_integrity()
