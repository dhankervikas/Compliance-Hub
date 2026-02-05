import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "."))

from app.database import Base
from app.config import settings
from app.models.control import Control
from app.models.process import Process, SubProcess, process_control_mapping

# Constants
TARGET_TENANT_ID = "a61624c9-b0d9-4125-9bd5-edf7af8fb78e"
FRAMEWORK_CODE = "ISO27001"

# MAPPING DICTIONARY (Clause/Annex -> Process Name)
# Based on standard ISO 27001 themes
MAPPING = {
    # Clause 4: Context
    "4.1": "Governance & Policy",
    "4.2": "Governance & Policy",
    "4.3": "Governance & Policy",
    "4.4": "Governance & Policy",
    # Clause 5: Leadership
    "5.1": "Governance & Policy",
    "5.2": "Governance & Policy",
    "5.3": "Governance & Policy",
    # Clause 6: Planning
    "6.1.1": "Risk Management",
    "6.1.2": "Risk Management",
    "6.1.3": "Risk Management",
    "6.2": "Governance & Policy",
    "6.3": "Incident & Resilience", # Change management
    # Clause 7: Support
    "7.1": "Governance & Policy", # Resources
    "7.2": "HR Security", # Competence
    "7.3": "HR Security", # Awareness
    "7.4": "Governance & Policy", # Communication
    "7.5.1": "Governance & Policy",
    "7.5.2": "Governance & Policy",
    "7.5.3": "Governance & Policy",
    # Clause 8: Operation
    "8.1": "Operations (General)",
    "8.2": "Risk Management",
    "8.3": "Risk Management",
    # Clause 9: Performance
    "9.1": "Governance & Policy", # Monitoring (General) - or Logging?
    "9.2.1": "Internal Audit",
    "9.2.2": "Internal Audit",
    "9.3.1": "Management Review",
    "9.3.2": "Management Review",
    "9.3.3": "Management Review",
    # Clause 10: Improvement
    "10.1": "Improvement",
    "10.2": "Improvement",
    
    # Annex A.5 - Organizational
    "A.5.1": "Governance & Policy",
    "A.5.2": "Governance & Policy",
    "A.5.3": "Governance & Policy", # Segregation
    "A.5.4": "Governance & Policy",
    "A.5.5": "Legal & Compliance",
    "A.5.6": "Legal & Compliance",
    "A.5.7": "Threat Intel",
    "A.5.8": "SDLC (Development)", # Project Mgmt security usually fits properly here or Gov
    "A.5.9": "Asset Management",
    "A.5.10": "Asset Management",
    "A.5.11": "HR Security", # Return of assets
    "A.5.12": "Asset Management", # Classification
    "A.5.13": "Asset Management", # Labelling
    "A.5.14": "Access Control (IAM)", # Info transfer? Or Network?
    "A.5.15": "Access Control (IAM)",
    "A.5.16": "Access Control (IAM)",
    "A.5.17": "Access Control (IAM)",
    "A.5.18": "Access Control (IAM)",
    "A.5.19": "Supplier Mgmt",
    "A.5.20": "Supplier Mgmt",
    "A.5.21": "Supplier Mgmt",
    "A.5.22": "Supplier Mgmt",
    "A.5.23": "Supplier Mgmt", # Cloud services
    "A.5.24": "Incident & Resilience",
    "A.5.25": "Incident & Resilience",
    "A.5.26": "Incident & Resilience",
    "A.5.27": "Incident & Resilience",
    "A.5.28": "Legal & Compliance", # Evidence? Or Incident?
    "A.5.29": "Incident & Resilience", # Disruption
    "A.5.30": "Incident & Resilience", # ICT readiness (BCP)
    "A.5.31": "Legal & Compliance",
    "A.5.32": "Legal & Compliance", # IP
    "A.5.33": "Legal & Compliance", # Records
    "A.5.34": "Legal & Compliance", # Privacy
    "A.5.35": "Internal Audit", # Independent review
    "A.5.36": "Legal & Compliance", # Compliance with policies
    "A.5.37": "Operations (General)",
    
    # Annex A.6 - People
    "A.6.1": "HR Security",
    "A.6.2": "HR Security",
    "A.6.3": "HR Security",
    "A.6.4": "HR Security",
    "A.6.5": "HR Security",
    "A.6.6": "HR Security",
    "A.6.7": "HR Security", # Remote working
    "A.6.8": "Incident & Resilience", # Event reporting - or Incident?

    # Annex A.7 - Physical
    "A.7.1": "Physical Security",
    "A.7.2": "Physical Security",
    "A.7.3": "Physical Security",
    "A.7.4": "Physical Security",
    "A.7.5": "Physical Security",
    "A.7.6": "Physical Security",
    "A.7.7": "Physical Security",
    "A.7.8": "Physical Security",
    "A.7.9": "Physical Security",
    "A.7.10": "Operations (General)", # Media
    "A.7.11": "Physical Security", # Utilities
    "A.7.12": "Physical Security", # Cabling
    "A.7.13": "Operations (General)", # Maintenance
    "A.7.14": "Asset Management", # Disposal

    # Annex A.8 - Tech
    "A.8.1": "Asset Management", # Endpoint
    "A.8.2": "Access Control (IAM)", # Privileged access
    "A.8.3": "Access Control (IAM)",
    "A.8.4": "SDLC (Development)", # Source Code
    "A.8.5": "Access Control (IAM)", # Auth
    "A.8.6": "Capacity Management",
    "A.8.7": "Operations (General)", # Malware - or Vuln mgmt?
    "A.8.8": "Vulnerability Management",
    "A.8.9": "Configuration Management", # Config
    "A.8.10": "Data Lifecycle Management", # Deletion
    "A.8.11": "Data Lifecycle Management", # Masking / Cryptography
    "A.8.12": "Network Security", # DLP?
    "A.8.13": "Backup Management",
    "A.8.14": "Incident & Resilience", # Redundancy
    "A.8.15": "Logging & Monitoring",
    "A.8.16": "Logging & Monitoring",
    "A.8.17": "Clock Synchronization",
    "A.8.18": "Access Control (IAM)", # Priv utility - or Ops?
    "A.8.19": "Operations (General)",
    "A.8.20": "Network Security",
    "A.8.21": "Network Security",
    "A.8.22": "Network Security",
    "A.8.23": "Network Security",
    "A.8.24": "Cryptography",
    "A.8.25": "SDLC (Development)",
    "A.8.26": "SDLC (Development)",
    "A.8.27": "SDLC (Development)",
    "A.8.28": "SDLC (Development)",
    "A.8.29": "SDLC (Development)",
    "A.8.30": "SDLC (Development)", # Outsourced Dev
    "A.8.31": "SDLC (Development)",
    "A.8.32": "Configuration Management", # Change mgmt
    "A.8.33": "SDLC (Development)", # Test info
    "A.8.34": "Internal Audit", # Audit tests
}

def remap_controls():
    print(f"[-] Starting REMAP_ISO_CONTROLS for {TARGET_TENANT_ID}...")
    
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Pre-Load Process Map
        procs = db.query(Process).all()
        proc_map = {p.name: p for p in procs} # Name -> Obj
        
        # Load Controls
        controls = db.query(Control).filter(Control.tenant_id == TARGET_TENANT_ID).all()
        
        updated_count = 0
        
        for c in controls:
             # Find Target Process
             target_proc_name = MAPPING.get(c.control_id)
             if not target_proc_name:
                 # Try partial?
                 continue
                 
             target_proc = proc_map.get(target_proc_name)
             if not target_proc:
                 print(f"[!] Process not found: {target_proc_name}")
                 continue
                 
             # 1. Update Category on Control (Denormalized)
             c.category = target_proc_name
             db.add(c)
             
             # 2. Update Linkage
             # Check for 'Controls' subprocess
             sp = db.query(SubProcess).filter(SubProcess.process_id == target_proc.id, SubProcess.name == "Controls").first()
             if not sp:
                 sp = SubProcess(name="Controls", process_id=target_proc.id)
                 db.add(sp)
                 db.commit()
                 db.refresh(sp)
             
             # Clear OLD mappings
             db.execute(process_control_mapping.delete().where(process_control_mapping.c.control_id == c.id))
             
             # Add NEW mapping
             db.execute(process_control_mapping.insert().values(subprocess_id=sp.id, control_id=c.id))
             
             updated_count += 1
             
        db.commit()
        print(f"[+] SUCCESS: Remapped {updated_count} controls.")
        
    except Exception as e:
        print(f"[!] Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    remap_controls()
