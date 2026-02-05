
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "."))

from app.database import Base
from app.config import settings
from app.models.control import Control
from app.models.process import Process

# Setup DB
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def verify_mappings():
    print("[-] Connecting to DB...")

    # Find ALL unmapped controls
    print("\n[-] Checking for Unmapped Controls (Process=None):")
    unmapped = []
    controls = db.query(Control).all()
    for c in controls:
        if not c.process_name:
            unmapped.append(f"{c.control_id} ({c.title})")
            
    if unmapped:
        print(f"[FAIL] Found {len(unmapped)} unmapped controls:")
        for u in unmapped[:20]: # Print first 20
            print(f"    {u}")
        if len(unmapped) > 20: print(f"    ... and {len(unmapped)-20} more.")
    else:
        print("[PASS] No unmapped controls found.")

    # Check for unwanted process
    perf_eval = db.query(Process).filter(Process.name == "Performance evaluation").first()
    if perf_eval:
         print("\n[FAIL] 'Performance evaluation' process still exists!")
         all_passed = False
    else:
         print("\n[PASS] 'Performance evaluation' process successfully removed.")
         
    # Check for new process
    clock_sync = db.query(Process).filter(Process.name == "Clock Synchronization").first()
    if clock_sync:
        print("\n[PASS] 'Clock Synchronization' process created.")
    else:
        print("\n[FAIL] 'Clock Synchronization' process missing!")
        all_passed = False

    if all_passed:
        print("\n[SUCCESS] All checks passed.")
    else:
        print("\n[FAILURE] One or more checks failed.")

if __name__ == "__main__":
    try:
        verify_mappings()
    finally:
        db.close()
