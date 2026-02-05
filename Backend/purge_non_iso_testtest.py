import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "."))

from app.database import Base
from app.config import settings
from app.models.control import Control
from app.models.framework import Framework
from app.models.process import process_control_mapping

# Constants
TARGET_TENANT_ID = "a61624c9-b0d9-4125-9bd5-edf7af8fb78e"
KEEP_FRAMEWORK_CODE = "ISO27001"

def purge_non_iso():
    print(f"[-] Starting PURGE_NON_ISO for {TARGET_TENANT_ID}...")
    
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Get ISO Framework ID
        iso = db.query(Framework).filter(Framework.code == KEEP_FRAMEWORK_CODE).first()
        if not iso:
            print("[!] ISO Framework not found!")
            return

        print(f"[-] Keeping Framework: {iso.name} (ID: {iso.id})")
        
        # Select Controls to Delete (All controls for this tenant NOT in ISO Framework)
        # Note: We must be careful not to delete global controls if they are shared (but tenant_id protects us)
        controls_to_delete = db.query(Control).filter(
            Control.tenant_id == TARGET_TENANT_ID,
            Control.framework_id != iso.id
        ).all()
        
        if not controls_to_delete:
            print("[+] No non-ISO controls found.")
            return

        count = len(controls_to_delete)
        print(f"[-] Found {count} controls to delete (SOC2, NIST, etc).")
        
        # Delete dependencies? (Mappings)
        # SQLAlchemy cascade might handle it, but let's be safe for Many-to-Many
        control_ids = [c.id for c in controls_to_delete]
        
        if control_ids:
             # Delete Mappings
             stmt = process_control_mapping.delete().where(process_control_mapping.c.control_id.in_(control_ids))
             db.execute(stmt)
             
             # Delete Controls
             db.query(Control).filter(Control.id.in_(control_ids)).delete(synchronize_session=False)
        
        db.commit()
        print(f"[+] SUCCESS: Purged {count} non-ISO controls.")
        
    except Exception as e:
        print(f"[!] Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    purge_non_iso()
