import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "."))

from app.database import Base
from app.config import settings
from app.models.universal_intent import UniversalIntent, IntentStatus
from app.models.intent_framework_crosswalk import IntentFrameworkCrosswalk, StandardProcessOverlay
from app.services.policy_intents import POLICY_CONTROL_MAP, POLICY_INTENTS

# Setup DB
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# Copied from seed_canonical_processes.py to avoid circular deps
INTENT_TO_PROCESS_MAP = {
    # Governance
    "ISMS Scope": "Governance & Policy",
    "Context of the Organization": "Governance & Policy",
    "Interested Parties": "Governance & Policy",
    "Information Security Policy": "Governance & Policy",
    "Management Commitment Statement": "Governance & Policy",
    "ISMS Roles and Responsibilities": "Governance & Policy",
    "Document Control Procedure": "Governance & Policy",
    "Documented information": "Governance & Policy",
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
    "Information Security Event Reporting": "HR Security",
    
    # Asset
    "Asset Management Policy": "Asset Management",
    "Acceptable Use Policy": "Asset Management",
    "Data Classification Policy": "Asset Management",
    "Information Deletion": "Asset Management",
    "Data Masking": "Asset Management",
    "Data Leakage Prevention": "Operations (General)", # FIXED Per Requirement
    "Secure Disposal": "Asset Management",
    "Storage Media": "Asset Management",
    "Security of Assets Off-Premises": "Asset Management",
    "Business Continuity Policy": "Incident & Resilience", # FIXED Per Requirement (A.5.29)

    # Access
    "Access Control Policy": "Access Control (IAM)",
    "Mobile Device Policy": "Access Control (IAM)",
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
    "Operations": "Operations (General)",
    "Protection Against Malware": "Operations (General)",
    "Software Installation": "Operations (General)",
    "Technical Vulnerabilities": "Vulnerability Management",
    "Operational Procedures": "Operations (General)",
    "Malware Protection": "Operations (General)",
    
    # Config
    "Configuration Management": "Configuration Management",
    "Change Management Policy": "Configuration Management",
    
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
    "Information Transfer": "Network Security",
    
    # SDLC
    "Secure Development Policy": "SDLC (Development)",
    "Testing": "SDLC (Development)",
    "Outsourced Development": "SDLC (Development)",
    "Separation of Environments": "SDLC (Development)",
    "System Change Control": "SDLC (Development)",
    "Test Data": "SDLC (Development)",
    
    # Supplier
    "Third-Party Security Policy": "Supplier Mgmt",
    "Information Security in Supplier Relationships": "Supplier Mgmt",
    "Supplier Security Policy": "Supplier Mgmt",
    "Supplier Security Agreements": "Supplier Mgmt",
    "ICT Supply Chain Management": "Supplier Mgmt",
    "Monitoring and Review of Supplier Services": "Supplier Mgmt",
    
    # Incident
    "Incident Response Policy": "Incident & Resilience",
    "Incident Management": "Incident & Resilience",
    "Evidence Collection": "Incident & Resilience",
    
    # Threat
    "Threat Intelligence": "Threat Intel",
    
    # Legal
    "Data Protection and Privacy Policy": "Legal & Compliance",
    "Legal and Compliance Requirements": "Legal & Compliance",
    "Independent Review of Information Security": "Legal & Compliance", # A.5.35 Fixed
    "Compliance with Legal and Contractual Requirements": "Legal & Compliance",
    "Intellectual Property Rights": "Legal & Compliance",
    "Protection of Records": "Legal & Compliance",
    "Privacy and Protection of PII": "Legal & Compliance",
    "Independent Review": "Legal & Compliance"
}

def seed_universal_intents():
    print("[-] Seeding Universal Intents & Crosswalk...")

    # Ensure tables exist 
    Base.metadata.create_all(bind=engine) 

    count_intents = 0
    count_crosswalk = 0

    # 1. Promote Policy Intents to Universal Intents
    # We use POLICY_INTENTS keys as the source
    for p_name, p_data in POLICY_INTENTS.items():
        canonical_process = INTENT_TO_PROCESS_MAP.get(p_name, "Governance & Policy")
        
        # Create/Get Universal Intent
        intent_id_str = f"INT-{p_name.upper().replace(' ', '-').replace('&', 'AND')[:30]}"
        
        intent = db.query(UniversalIntent).filter(UniversalIntent.intent_id == intent_id_str).first()
        if not intent:
            intent = UniversalIntent(
                intent_id=intent_id_str,
                description=p_data.get('description', f"Intent for {p_name}"),
                category=canonical_process,
                status=IntentStatus.PENDING
            )
            db.add(intent)
            db.commit()
            db.refresh(intent)
            count_intents += 1
            # print(f"    [+] Created Intent: {p_name}")
        
        # 2. Populate Crosswalk from POLICY_CONTROL_MAP
        control_ids = POLICY_CONTROL_MAP.get(p_name, [])
        for cid in control_ids:
            # Determine framework from Control ID prefix
            fw_id = "UNKNOWN"
            if cid.startswith("A.") or cid.startswith("ISO_") or cid.startswith("Clause"):
                fw_id = "ISO_27001"
            elif cid.startswith("CC") or cid.startswith("P") or cid.startswith("PI"):
                fw_id = "SOC2"
            
            # Check exist
            exists = db.query(IntentFrameworkCrosswalk).filter(
                IntentFrameworkCrosswalk.intent_id == intent.id,
                IntentFrameworkCrosswalk.framework_id == fw_id,
                IntentFrameworkCrosswalk.control_reference == cid
            ).first()
            
            if not exists:
                cw = IntentFrameworkCrosswalk(
                    intent_id=intent.id,
                    framework_id=fw_id,
                    control_reference=cid
                )
                db.add(cw)
                count_crosswalk += 1
    
    db.commit()
    print(f"[SUCCESS] Seeded {count_intents} Universal Intents and {count_crosswalk} Crosswalk Entries.")

    # 3. Seed Standard Process Overlays (Dynamic Metadata)
    print("[-] Seeding Standard Process Overlays...")
    from app.models.process import Process # Ensure we have Canonical names if needed
    
    # ISO 27001 Overlays
    iso_overlays = [
        ("HR Security", "Annex A.6: People Controls", 6),
        ("Asset Management", "Annex A.8: Technological Controls (Assets)", 8),
        ("Access Control (IAM)", "Annex A.5: Organizational Controls (Access)", 5),
        ("Physical Security", "Annex A.7: Physical Controls", 7),
        ("Operations (General)", "Annex A.8: Technological Controls (Ops)", 8),
        ("Legal & Compliance", "Clause 4 & Annex A.5 (Legal)", 4),
        ("Governance & Policy", "Clause 5: Leadership", 5),
        ("Risk Management", "Clause 6: Planning", 6)
    ]
    
    for proc_name, label, order in iso_overlays:
        exists = db.query(StandardProcessOverlay).filter(
            StandardProcessOverlay.framework_id == "ISO_27001",
            StandardProcessOverlay.process_name == proc_name
        ).first()
        
        if not exists:
            overlay = StandardProcessOverlay(
                framework_id="ISO_27001",
                process_name=proc_name,
                external_label=label,
                display_order=order
            )
            db.add(overlay)
    
    db.commit()
    print("[SUCCESS] Seeding Complete.")

if __name__ == "__main__":
    try:
        seed_universal_intents()
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()
