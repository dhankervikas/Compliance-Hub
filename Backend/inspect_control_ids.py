import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import Base, get_db
from app.models.control import Control

# Setup Database
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def inspect_ids():
    session = SessionLocal()
    try:
        ACTIVE_ISO_ID = 13
        print(f"--- Inspecting Controls for Framework ID {ACTIVE_ISO_ID} ---")
        controls = session.query(Control).filter(Control.framework_id == ACTIVE_ISO_ID).all()
        print(f"Total Controls Found: {len(controls)}")
        
        # Print first 10
        print("\n--- First 10 Control IDs ---")
        for c in controls[:10]:
            print(f"ID: {c.id} | ControlID: '{c.control_id}' | Title: '{c.title[:30]}...'")
            
        # Check for A. prefix
        a_count = sum(1 for c in controls if c.control_id.startswith('A.'))
        digit_count = sum(1 for c in controls if c.control_id[0].isdigit())
        print(f"\nStats: Starts with 'A.': {a_count} | Starts with Digit: {digit_count}")
        
    finally:
        session.close()

if __name__ == "__main__":
    inspect_ids()
