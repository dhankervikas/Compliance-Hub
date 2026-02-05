import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import Base, get_db
from app.models.framework import Framework
# Import Control to cascade delete if necessary, though frameworks usually cascade
from app.models.control import Control 

# Setup Database
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def cleanup_duplicates():
    session = SessionLocal()
    try:
        # The stale tenant ID identified from inspection
        STALE_TENANT_ID = '5c388945-3ebb-4856-99d9-ebf2f448ae73'
        
        print(f"--- Cleaning up stale frameworks for Tenant: {STALE_TENANT_ID} ---")
        
        frameworks_to_delete = session.query(Framework).filter(Framework.tenant_id == STALE_TENANT_ID).all()
        
        if not frameworks_to_delete:
            print("No frameworks found for the stale tenant.")
            return

        print(f"Found {len(frameworks_to_delete)} frameworks to delete.")
        
        for f in frameworks_to_delete:
            print(f"Deleting: ID={f.id}, Code='{f.code}', Name='{f.name}'")
            # Manually delete controls if cascade isn't set up, just to be safe
            controls_count = session.query(Control).filter(Control.framework_id == f.id).delete()
            print(f" - Deleted {controls_count} related controls.")
            
            session.delete(f)
            
        session.commit()
        print("--- Cleanup Complete: Stale records removed. ---")
            
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    cleanup_duplicates()
