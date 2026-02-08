
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.join(os.path.dirname(__file__), "."))

from app.database import Base
from app.config import settings
from app.models.process import Process, SubProcess
from app.models.control import Control

# Setup DB
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# User defined mapping for verification
USER_MAPPING = {
    "Governance": ["ISO_4.1", "ISO_4.2", "ISO_4.3", "ISO_4.4", "ISO_5.1", "ISO_5.2", "ISO_5.3", "ISO_7.1", "ISO_7.5.1", "ISO_7.5.2", "ISO_7.5.3", "A.5.1", "A.5.2", "A.5.3", "A.5.4", "A.5.5", "A.5.6", "A.5.37"],
    "Risk Management": ["ISO_6.1.1", "ISO_6.1.2", "ISO_6.1.3", "ISO_6.3", "ISO_8.1", "ISO_8.2", "ISO_8.3"], # Updated 6.1 -> 6.1.1
    "IT Operations": ["A.8.1", "A.8.7", "A.8.10", "A.8.18", "A.8.19"], # Was Operations
    "Performance Evaluation": ["ISO_6.2", "ISO_9.1", "ISO_9.2.1", "ISO_9.2.2", "ISO_9.3.1", "ISO_9.3.2", "ISO_9.3.3", "A.8.34"],
    "Improvement": ["ISO_10.1", "ISO_10.2"],
    "Human Resources Management": ["ISO_7.2", "ISO_7.3", "A.6.1", "A.6.2", "A.6.3", "A.6.4", "A.6.5", "A.6.6", "A.6.7", "A.6.8"], # Was HR Security
    "Asset Management": ["A.5.9", "A.5.10", "A.5.11", "A.5.12", "A.5.13", "A.7.10", "A.7.14"],
    "Access Management": ["A.5.15", "A.5.16", "A.5.17", "A.5.18", "A.8.2", "A.8.3", "A.8.4", "A.8.5"], # Was Access Control (IAM)
    "Physical Security": ["A.7.1", "A.7.2", "A.7.3", "A.7.4", "A.7.5", "A.7.6", "A.7.7", "A.7.8", "A.7.9", "A.7.11", "A.7.12", "A.7.13"],
    "Configuration Management": ["A.8.9"],
    "Cryptography": ["A.8.11", "A.8.12", "A.8.24"],
    "Logging & Monitoring": ["A.8.15", "A.8.16"],
    "Clock Synchronization": ["A.8.17"],
    "Vulnerability Management": ["A.8.8"],
    "Capacity Management": ["A.8.6"],
    "Backup Management": ["A.8.13"],
    "Network Security": ["A.8.20", "A.8.21", "A.8.22", "A.8.23", "A.5.14"],
    "Secure Software Development Life Cycle (SSDLC)": ["A.8.25", "A.8.26", "A.8.27", "A.8.28", "A.8.29", "A.8.30", "A.8.31", "A.8.32", "A.8.33", "A.5.8"],
    "Third Party Risk Management": ["A.5.19", "A.5.20", "A.5.21", "A.5.22", "A.5.23"], # Was Supplier Mgmt
    "Incident & Resilience": ["ISO_7.4", "A.5.24", "A.5.25", "A.5.26", "A.5.27", "A.5.28", "A.5.29", "A.5.30", "A.8.14"],
    "Threat Intelligence": ["A.5.7"], # Was Threat Intel
    "Legal & Compliance": ["A.5.31", "A.5.32", "A.5.33", "A.5.34", "A.5.35", "A.5.36"]
}

def verify_mappings():
    print("[-] Verifying Process Control Mappings...")
    all_passed = True
    
    for process_name, expected_controls in USER_MAPPING.items():
        proc = db.query(Process).filter(Process.name == process_name).first()
        if not proc:
            print(f"[FAIL] Process '{process_name}' not found!")
            all_passed = False
            continue
            
        found_controls = []
        for sp in proc.sub_processes:
            for c in sp.controls:
                # Normalize ID: "ISO_9.1" -> "9.1" checking
                cid = c.control_id.replace("ISO_", "")
                found_controls.append(cid)
        
        # Check for missing controls
        missing = []
        for exp in expected_controls:
            exp_clean = exp.replace("ISO_", "")
            if exp_clean not in found_controls:
                # Try prefix check for A. controls sometimes stored without A. or with prefix
                if not any(fc == exp_clean or fc.endswith(exp_clean) for fc in found_controls):
                    missing.append(exp)
        
        if missing:
            print(f"[FAIL] {process_name}: Missing controls {missing}")
            # print(f"       Found: {found_controls}")
            all_passed = False
        else:
            print(f"[PASS] {process_name}: All {len(expected_controls)} controls found.")

    if all_passed:
        print("\n[SUCCESS] All process mappings verified successfully!")
    else:
        print("\n[FAIL] Some process mappings are incorrect.")

if __name__ == "__main__":
    try:
        verify_mappings()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()
