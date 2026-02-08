
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "."))

from app.database import Base
from app.config import settings
from app.models.process import Process, SubProcess
from app.models.control import Control
from app.services.policy_intents import POLICY_CONTROL_MAP

# Setup DB
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def seed_canonical_processes():
    print("[-] Seeding 22 Canonical Processes...")
    
    # 1. Define the 22 Canonical Processes
    CANONICAL_PROCESSES = [
        "Governance & Policy",
        "HR Security",
        "Asset Management",
        "Access Control (IAM)",
        "Physical Security",
        "Operations",
        "Configuration Management",
        "Cryptography",
        "Logging & Monitoring",
        "Clock Synchronization",
        "Vulnerability Management",
        "Capacity Management",
        "Backup Management",
        "Network Security",
        "SDLC (Development)",
        "Supplier Mgmt",
        "Incident & Resilience",
        "Threat Intel",
        "Legal & Compliance",
        "Risk Management",
	"Performance Evaluation",
        "Improvement"
    ]
    
    # 2. Define Mapping: Policy/Intent Name -> Canonical Process
    # This maps the keys from POLICY_CONTROL_MAP to the list above
    INTENT_TO_PROCESS_MAP = {
        # Governance
        "ISMS Scope": "Governance & Policy",
        "Context of the Organization": "Governance & Policy",
        "Interested Parties": "Governance & Policy",
        "Information Security Policy": "Governance & Policy",
        "Management Commitment Statement": "Governance & Policy",
        "ISMS Roles and Responsibilities": "Governance & Policy",
        "Document Control Procedure": "Governance & Policy",
        "Documented information": "Governance & Policy", # If exists
        "Security in Project Management": "Governance & Policy",
        
        # Risk
        "Risk Assessment Methodology": "Risk Management",
        "Risk Treatment Plan": "Risk Management",
        "Statement of Applicability (SoA)": "Risk Management",
        "Information Security Objectives": "Risk Management",
        
        # HR
        "Competence and Awareness Policy": "HR Security",
        "Information Security Training Program": "HR Security",
        "Screening": "HR Security",
        "Terms and Conditions of Employment": "HR Security",
        "Disciplinary Process": "HR Security",
        "Responsibilities After Termination": "HR Security",
        "Confidentiality Agreements": "HR Security",
        "Teleworking": "HR Security",
        "Information Security Event Reporting": "HR Security", # Could be incident, but often HR
        
        # Asset
        "Asset Management Policy": "Asset Management",
        "Acceptable Use Policy": "Asset Management",
        "Data Classification Policy": "Asset Management",
        "Information Deletion": "Asset Management",
        "Data Masking": "Asset Management", # Or Crypto? Asset fits well for classification
        "Data Leakage Prevention": "Asset Management", # Or Ops
        "Secure Disposal": "Asset Management",
        "Storage Media": "Asset Management",
        "Security of Assets Off-Premises": "Asset Management",

        # Access
        "Access Control Policy": "Access Control (IAM)",
        "Mobile Device Policy": "Access Control (IAM)", # Often grouped here
        "Password Policy": "Access Control (IAM)",
        "Remote Access Policy": "Access Control (IAM)",
        "User Endpoint Devices": "Access Control (IAM)",
        "Privileged Access Rights": "Access Control (IAM)",
        "Information Access Restriction": "Access Control (IAM)",
        "Access to Source Code": "Access Control (IAM)",
        "Secure Authentication": "Access Control (IAM)",
        "Use of Privileged Utility Programs": "Access Control (IAM)",
        
        # Physical
        "Physical Security Policy": "Physical Security",
        "Physical Entry Controls": "Physical Security",
        "Securing Offices and Facilities": "Physical Security",
        "Working in Secure Areas": "Physical Security",
        "Desk and Screen Policy": "Physical Security",
        "Equipment Siting and Protection": "Physical Security",
        "Supporting Utilities": "Physical Security",
        "Cabling Security": "Physical Security",
        "Equipment Maintenance": "Physical Security",
        
        # Operations
        "Operations": "Operations",
        "Protection Against Malware": "Operations",
        "Software Installation": "Operations",
        "Technical Vulnerabilities": "Vulnerability Management", # Specific map
        "Operational Procedures": "Operations",
        "Malware Protection": "Operations",
        
        # Config
        "Configuration Management": "Configuration Management", # From Policy map
        "Change Management Policy": "Configuration Management", # Or Ops
        
        # Crypto
        "Cryptography Policy": "Cryptography",
        
        # Logging
        "Logging and Monitoring": "Logging & Monitoring",
        "Clock Synchronization": "Clock Synchronization",
        
        # Vuln
        "Vulnerability Management Policy": "Vulnerability Management",
        
        # Capacity
        "Capacity Management": "Capacity Management",
        
        # Backup
        "Backup and Recovery Policy": "Backup Management",
        
        # Network
        "Network Security Policy": "Network Security",
        "Networks Segregation": "Network Security",
        "Web Filtering": "Network Security",
        "Network Security Management": "Network Security",
        "Information Transfer": "Network Security", # Or Asset
        
        # SDLC
        "Secure Development Policy": "SDLC (Development)",
        "Testing": "SDLC (Development)",
        "Outsourced Development": "SDLC (Development)",
        "Separation of Environments": "SDLC (Development)",
        "System Change Control": "SDLC (Development)",
        "Test Data": "SDLC (Development)",
        # "Access to Source Code" mapped to Access Control above, could be here too.
        
        # Supplier
        "Third-Party Security Policy": "Supplier Mgmt",
        "Information Security in Supplier Relationships": "Supplier Mgmt",
        "Supplier Security Policy": "Supplier Mgmt",
        "Supplier Security Agreements": "Supplier Mgmt",
        "ICT Supply Chain Management": "Supplier Mgmt",
        "Monitoring and Review of Supplier Services": "Supplier Mgmt",
        
        # Incident
        "Incident Response Policy": "Incident & Resilience",
        "Business Continuity Policy": "Incident & Resilience",
        "Incident Management": "Incident & Resilience",
        "Evidence Collection": "Incident & Resilience",
        
        # Threat
        "Threat Intelligence": "Threat Intel",
        # "Threat Intelligence" might appear in Risk Policy, but let's check
        # ISO A.5.7 is threat intel.
        
        # Legal
        "Data Protection and Privacy Policy": "Legal & Compliance",
        "Legal and Compliance Requirements": "Legal & Compliance",
        "Independent Review of Information Security": "Legal & Compliance",
        "Compliance with Legal and Contractual Requirements": "Legal & Compliance",
        "Intellectual Property Rights": "Legal & Compliance",
        "Protection of Records": "Legal & Compliance",
        "Privacy and Protection of PII": "Legal & Compliance",
        
        # Performance Evaluation
        "Monitoring and Measurement": "Performance Evaluation",
        "Internal Audit Program": "Performance Evaluation",
        "Management Review": "Performance Evaluation",
        "Independent Review": "Legal & Compliance", # Keep this as Legal if preferred, or move to Performance if it fits A.18
        
        # Improvement
        # "Corrective Action" etc.
    }
    
    # 3. Clear Existing
    print("[-] Clearing existing process data...")
    db.execute(text("DELETE FROM process_control_mapping"))
    db.execute(text("DELETE FROM sub_processes"))
    db.execute(text("DELETE FROM processes"))
    db.commit()
    
    # 4. Create Canonical Processes
    process_obj_map = {}
    for p_name in CANONICAL_PROCESSES:
        p = Process(name=p_name, description=f"Canonical Process: {p_name}")
        db.add(p)
        db.commit()
        db.refresh(p)
        process_obj_map[p_name] = p
        
    print(f"[+] Created {len(process_obj_map)} Canonical Processes.")
    
    # 5. Create SubProcesses (Policies) and Map Controls
    mapped_subprocs = 0
    mapped_controls = 0
    
    for intent_name, control_ids in POLICY_CONTROL_MAP.items():
        # Find parent
        parent_name = INTENT_TO_PROCESS_MAP.get(intent_name)
        
        # Fallback for unmapped items -> "Governance and Policy" or "Operations"
        if not parent_name:
            if "Policy" in intent_name: parent_name = "Governance and Policy"
            else: parent_name = "Operations"
            # print(f"Warning: Unmapped Intent '{intent_name}' -> Defaulting to {parent_name}")
            
        parent_proc = process_obj_map.get(parent_name)
        if not parent_proc:
            # Should not happen if map is consistent
            print(f"Error: Parent Process '{parent_name}' not found for '{intent_name}'")
            continue
            
        # Create SubProcess
        sp = SubProcess(name=intent_name, description="Policy Intent Group", process_id=parent_proc.id)
        db.add(sp)
        db.commit()
        db.refresh(sp)
        mapped_subprocs += 1
        
        # Map Controls
        valid_controls = []
        for cid in control_ids:
            c = db.query(Control).filter(Control.control_id == cid).first()
            if not c and cid.startswith("ISO_"):
                 c = db.query(Control).filter(Control.control_id == cid.replace("ISO_", "")).first()
            
            if c:
                valid_controls.append(c)
                # Sync category for Frontend Badge
                c.category = parent_proc.name
                db.add(c) # key to ensure update is tracked
        
        if valid_controls:
            sp.controls.extend(valid_controls)
            mapped_controls += len(valid_controls)
            
    db.commit()
    print(f"[SUCCESS] Mapped {mapped_subprocs} Intents (SubProcesses) and {mapped_controls} Controls.")

if __name__ == "__main__":
    try:
        seed_canonical_processes()
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()
