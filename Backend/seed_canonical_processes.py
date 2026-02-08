
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
        "Governance", # Was Governance & Policy
        "Risk Management",
        "IT Operations", # Was Operations
        "Performance Evaluation",
        "Improvement",
        "Human Resources Management", # Was HR Security
        "Asset Management",
        "Access Management", # Was Access Control (IAM)
        "Physical Security",
        "Configuration Management",
        "Cryptography",
        "Logging & Monitoring",
        "Clock Synchronization",
        "Vulnerability Management",
        "Capacity Management",
        "Backup Management",
        "Network Security",
        "Secure Software Development Life Cycle (SSDLC)",
        "Third Party Risk Management", # Was Supplier Mgmt
        "Incident & Resilience",
        "Threat Intelligence", # Was Threat Intel
        "Legal & Compliance"
    ]
    
    # 2. Define Mapping: Policy/Intent Name -> Canonical Process
    # This maps the keys from POLICY_CONTROL_MAP to the list above
    INTENT_TO_PROCESS_MAP = {
        # Governance & Policy
        "ISMS Scope": "Governance",
        "Context of the Organization": "Governance",
        "Interested Parties": "Governance",
        "Information Security Policy": "Governance",
        "Management Commitment Statement": "Governance",
        "ISMS Roles and Responsibilities": "Governance",
        "Document Control Procedure": "Governance",
        "Documented information": "Governance", # If exists
        "Security in Project Management": "Secure Software Development Life Cycle (SSDLC)", # Moved to SDLC per user
        
        # Risk Management
        "Risk Assessment Methodology": "Risk Management",
        "Risk Treatment Plan": "Risk Management",
        "Statement of Applicability (SoA)": "Risk Management",
        "Operational Procedures": "Risk Management", # 8.1 Operational planning -> Risk (User list has 8.1 under Risk)
        # "Information Security Objectives": "Performance Evaluation", # 6.2 moved
        
        # HR Security
        "Competence and Awareness Policy": "Human Resources Management",
        "Information Security Training Program": "Human Resources Management",
        "Screening": "Human Resources Management",
        "Terms and Conditions of Employment": "Human Resources Management",
        "Disciplinary Process": "Human Resources Management",
        "Responsibilities After Termination": "Human Resources Management",
        "Confidentiality Agreements": "Human Resources Management",
        "Teleworking": "Human Resources Management",
        "Information Security Event Reporting": "Human Resources Management",
        
        # Asset Management
        "Asset Management Policy": "Asset Management",
        "Acceptable Use Policy": "Asset Management",
        "Data Classification Policy": "Asset Management",
        "Information Deletion": "IT Operations", # Per user list: A.8.10 is Operations
        "Data Masking": "Cryptography", # Per user list: A.8.11 is Crypto
        "Data Leakage Prevention": "Cryptography", # Per user list: A.8.12 is Crypto
        "Secure Disposal": "Asset Management",
        "Storage Media": "Asset Management",
        "Security of Assets Off-Premises": "Physical Security", # Per user list: A.7.9 -> Physical
        
        # Access Control (IAM)
        "Access Control Policy": "Access Management",
        "Mobile Device Policy": "Access Management", 
        "Password Policy": "Access Management",
        "Remote Access Policy": "Access Management",
        "User Endpoint Devices": "IT Operations", # A.8.1 -> Operations per user
        "Privileged Access Rights": "Access Management",
        "Information Access Restriction": "Access Management",
        "Access to Source Code": "Access Management",
        "Secure Authentication": "Access Management",
        "Use of Privileged Utility Programs": "IT Operations", # A.8.18 -> Operations per user
        
        # Physical Security
        "Physical Security Policy": "Physical Security",
        "Physical Entry Controls": "Physical Security",
        "Securing Offices and Facilities": "Physical Security",
        "Working in Secure Areas": "Physical Security",
        "Desk and Screen Policy": "Physical Security",
        "Protecting against physical and environmental threats": "Physical Security",
        "Working in secure areas": "Physical Security",
        "Equipment Siting and Protection": "Physical Security",
        # "Supporting Utilities" -> Physical
        "Supporting Utilities": "Physical Security",
        "Cabling Security": "Physical Security",
        "Equipment Maintenance": "Physical Security",
        
        # Operations
        "Operations": "IT Operations",
        "Protection Against Malware": "IT Operations",
        "Software Installation": "IT Operations",
        "Operational Procedures": "Risk Management", # Moved to Risk above, removing from here if duplicate or ensuring it's not here
        "Malware Protection": "IT Operations",
        
        # Configuration Management
        "Configuration Management": "Configuration Management",
        "Change Management Policy": "Secure Software Development Life Cycle (SSDLC)", # A.8.32 -> SDLC per user
        
        # Cryptography
        "Cryptography Policy": "Cryptography",
        
        # Logging & Monitoring
        "Logging and Monitoring": "Logging & Monitoring", # A.8.15, A.8.16
        
        # Clock Sync
        "Clock Synchronization": "Clock Synchronization",
        
        # Vulnerability Management
        "Vulnerability Management Policy": "Vulnerability Management",
        
        # Capacity Management
        "Capacity Management": "Capacity Management",
        
        # Backup Management
        "Backup and Recovery Policy": "Backup Management",
        
        # Network Security
        "Network Security Policy": "Network Security",
        "Networks Segregation": "Network Security",
        "Web Filtering": "Network Security",
        "Information Transfer": "Network Security",
        
        # SDLC (Development)
        "Secure Development Policy": "Secure Software Development Life Cycle (SSDLC)",
        "Testing": "Secure Software Development Life Cycle (SSDLC)",
        "Outsourced Development": "Secure Software Development Life Cycle (SSDLC)",
        "Separation of Environments": "Secure Software Development Life Cycle (SSDLC)",
        # "Test Data": "SDLC (Development)", 
        
        # Supplier Mgmt
        "Third-Party Security Policy": "Third Party Risk Management",
        "Information Security in Supplier Relationships": "Third Party Risk Management",
        "Supplier Security Agreements": "Third Party Risk Management",
        "ICT Supply Chain Management": "Third Party Risk Management",
        "Monitoring and Review of Supplier Services": "Third Party Risk Management",
        
        # Incident & Resilience
        "Incident Response Policy": "Incident & Resilience",
        "Communication": "Incident & Resilience", # Mapped to Incident controls in Intents
        "Business Continuity Policy": "Incident & Resilience", 
        "Incident Management": "Incident & Resilience",
        "Evidence Collection": "Incident & Resilience",
        
        # Threat Intel
        "Threat Intelligence": "Threat Intelligence",
        
        # Legal & Compliance
        "Data Protection and Privacy Policy": "Legal & Compliance",
        "Legal and Compliance Requirements": "Legal & Compliance",
        "Independent Review": "Legal & Compliance",
        "Intellectual Property Rights": "Legal & Compliance",
        "Protection of Records": "Legal & Compliance",
        
        # Performance Evaluation
        "Monitoring and Measurement": "Performance Evaluation",
        "Internal Audit Program": "Performance Evaluation",
        "Management Review": "Performance Evaluation",
        "Information Security Objectives": "Performance Evaluation", # 6.2 -> Performance per user
        
        # Improvement
        "Continual Improvement": "Improvement",
        "Nonconformity and Corrective Action": "Improvement"
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
        
        # Fallback for unmapped items -> "Governance" or "IT Operations"
        if not parent_name:
            if "Policy" in intent_name: parent_name = "Governance"
            else: parent_name = "IT Operations"
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
