import sys
import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "."))

from app.database import Base
from app.config import settings
from app.models.control import Control
from app.models.framework import Framework
from app.models.process import Process, SubProcess, process_control_mapping
from app.models.universal_intent import UniversalIntent, IntentStatus
from app.models.intent_framework_crosswalk import IntentFrameworkCrosswalk

# Constants
MASTER_FILE = r"C:\Projects\Compliance_Product\Backend\MASTER_ISO27001_INTENTS.csv"
ISO_FRAMEWORK_CODE = "ISO27001"
TARGET_TENANT_ID = "a61624c9-b0d9-4125-9bd5-edf7af8fb78e" # TestTest

# Official ISO 27001:2022 Standard Names (For Title)
ISO_STANDARDS = {
    # Include all 4-10 and A.5-A.8 from previous step
    "4.1": "Understanding the organization and its context",
    "4.2": "Understanding the needs and expectations of interested parties",
    "4.3": "Determining the scope of the information security management system",
    "4.4": "Information security management system",
    "5.1": "Leadership and commitment",
    "5.2": "Policy",
    "5.3": "Organizational roles, responsibilities and authorities",
    "6.1.1": "General",
    "6.1.2": "Information security risk assessment",
    "6.1.3": "Information security risk treatment",
    "6.2": "Information security objectives and planning to achieve them",
    "6.3": "Planning of changes",
    "7.1": "Resources",
    "7.2": "Competence",
    "7.3": "Awareness",
    "7.4": "Communication",
    "7.5.1": "General",
    "7.5.2": "Creating and updating",
    "7.5.3": "Control of documented information",
    "8.1": "Operational planning and control",
    "8.2": "Information security risk assessment",
    "8.3": "Information security risk treatment",
    "9.1": "Monitoring, measurement, analysis and evaluation",
    "9.2.1": "General",
    "9.2.2": "Internal audit programme",
    "9.3.1": "General",
    "9.3.2": "Management review inputs",
    "9.3.3": "Management review results",
    "10.1": "Continual improvement",
    "10.2": "Nonconformity and corrective action",
    "A.5.1": "Policies for information security",
    "A.5.2": "Information security roles and responsibilities",
    "A.5.3": "Segregation of duties",
    "A.5.4": "Management responsibilities",
    "A.5.5": "Contact with authorities",
    "A.5.6": "Contact with special interest groups",
    "A.5.7": "Threat intelligence",
    "A.5.8": "Information security in project management",
    "A.5.9": "Inventory of information and other associated assets",
    "A.5.10": "Acceptable use of information and other associated assets",
    "A.5.11": "Return of assets",
    "A.5.12": "Classification of information",
    "A.5.13": "Labelling of information",
    "A.5.14": "Information transfer",
    "A.5.15": "Access control",
    "A.5.16": "Identity management",
    "A.5.17": "Authentication information",
    "A.5.18": "Access rights",
    "A.5.19": "Information security in supplier relationships",
    "A.5.20": "Addressing information security within supplier agreements",
    "A.5.21": "Managing information security in the ICT supply chain",
    "A.5.22": "Monitoring, review and change management of supplier services",
    "A.5.23": "Information security for use of cloud services",
    "A.5.24": "Information security incident management planning and preparation",
    "A.5.25": "Assessment and decision on information security events",
    "A.5.26": "Response to information security incidents",
    "A.5.27": "Learning from information security incidents",
    "A.5.28": "Collection of evidence",
    "A.5.29": "Information security during disruption",
    "A.5.30": "ICT readiness for business continuity",
    "A.5.31": "Legal, statutory, regulatory and contractual requirements",
    "A.5.32": "Intellectual property rights",
    "A.5.33": "Protection of records",
    "A.5.34": "Privacy and protection of PII",
    "A.5.35": "Independent review of information security",
    "A.5.36": "Compliance with policies, rules and standards for information security",
    "A.5.37": "Documented operating procedures",
    "A.6.1": "Screening",
    "A.6.2": "Terms and conditions of employment",
    "A.6.3": "Information security awareness, education and training",
    "A.6.4": "Disciplinary process",
    "A.6.5": "Responsibilities after termination or change of employment",
    "A.6.6": "Confidentiality or non-disclosure agreements",
    "A.6.7": "Remote working",
    "A.6.8": "Information security event reporting",
    "A.7.1": "Physical security perimeters",
    "A.7.2": "Physical entry",
    "A.7.3": "Securing offices, rooms and facilities",
    "A.7.4": "Physical security monitoring",
    "A.7.5": "Protecting against physical and environmental threats",
    "A.7.6": "Working in secure areas",
    "A.7.7": "Clear desk and clear screen",
    "A.7.8": "Equipment siting and protection",
    "A.7.9": "Security of assets off-premises",
    "A.7.10": "Storage media",
    "A.7.11": "Supporting utilities",
    "A.7.12": "Cabling security",
    "A.7.13": "Equipment maintenance",
    "A.7.14": "Secure disposal or re-use of equipment",
    "A.8.1": "User endpoint devices",
    "A.8.2": "Privileged access rights",
    "A.8.3": "Information access restriction",
    "A.8.4": "Access to source code",
    "A.8.5": "Secure authentication",
    "A.8.6": "Capacity management",
    "A.8.7": "Protection against malware",
    "A.8.8": "Management of technical vulnerabilities",
    "A.8.9": "Configuration management",
    "A.8.10": "Information deletion",
    "A.8.11": "Data masking",
    "A.8.12": "Data leakage prevention",
    "A.8.13": "Information backup",
    "A.8.14": "Redundancy of information processing facilities",
    "A.8.15": "Logging",
    "A.8.16": "Monitoring activities",
    "A.8.17": "Clock synchronization",
    "A.8.18": "Use of privileged utility programs",
    "A.8.19": "Installation of software on operational systems",
    "A.8.20": "Networks security",
    "A.8.21": "Security of network services",
    "A.8.22": "Segregation of networks",
    "A.8.23": "Web filtering",
    "A.8.24": "Use of cryptography",
    "A.8.25": "Secure development life cycle",
    "A.8.26": "Application security requirements",
    "A.8.27": "Secure system architecture and engineering principles",
    "A.8.28": "Secure coding",
    "A.8.29": "Security testing in development and acceptance",
    "A.8.30": "Outsourced development",
    "A.8.31": "Separation of development, test and production environments",
    "A.8.32": "Change management",
    "A.8.33": "Test information",
    "A.8.34": "Protection of information systems during audit testing",
}

def restructure_controls():
    print("[-] Starting RESTRUCTURE_ISO_CONTROLS...")
    
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 1. Verification of Framework
        iso_fw = db.query(Framework).filter(Framework.code == ISO_FRAMEWORK_CODE).first()
        if not iso_fw:
             print("[!] ISO27001 missing.")
             return

        # 2. DELETE Existing Controls (The 690 Granular ones)
        print("[-] Deleting current ISO 27001 Controls (Granular View)...")
        # Only for ISO framework
        deleted = db.query(Control).filter(Control.framework_id == iso_fw.id, Control.tenant_id == TARGET_TENANT_ID).delete()
        db.commit()
        print(f"[+] Deleted {deleted} controls.")
        
        # 3. Ingest Master File
        print(f"[-] Reading Master File: {MASTER_FILE}")
        df = pd.read_csv(MASTER_FILE)
        
        # 4. Group by Clause (To create Standard Controls)
        grouped = df.groupby('Clause_or_control')
        
        # Process Map
        all_procs = db.query(Process).all()
        proc_lookup = {p.name: p for p in all_procs}
        
        controls_created = 0
        intents_upserted = 0
        links_created = 0
        
        for clause_id, group_df in grouped:
            clause_id = str(clause_id).strip()
            if not clause_id or clause_id == 'nan':
                continue
                
            # A. Create Standard Control
            # Title = "A.5.1 Policies for information security"
            # Standard Name
            std_name = ISO_STANDARDS.get(clause_id)
            if not std_name and f"A.{clause_id}" in ISO_STANDARDS:
                 # Helper logic for numeric annex
                 std_name = ISO_STANDARDS[f"A.{clause_id}"]
                 clause_id = f"A.{clause_id}"
            
            if not std_name:
                 # Fallback title if not in known map (should be rare for master file)
                 std_name = "Requirement"
                 
            # Determine Process (Majority Vote)
            # Find most common 'Process' in the group rows
            dominant_process_name = group_df['Process'].mode().iloc[0] if not group_df['Process'].empty else 'Uncategorized'
            
            control = Control(
                 control_id=clause_id, # e.g. A.5.1
                 title=f"{clause_id} {std_name}", 
                 description=std_name, 
                 status="not_started",
                 framework_id=iso_fw.id,
                 category=dominant_process_name,
                 tenant_id=TARGET_TENANT_ID
            )
            db.add(control)
            db.commit()
            db.refresh(control)
            controls_created += 1
            
            # Map Control to Process
            proc_obj = proc_lookup.get(dominant_process_name)
            if proc_obj:
                 # Link
                 sp = db.query(SubProcess).filter(SubProcess.process_id == proc_obj.id, SubProcess.name == "Controls").first()
                 if not sp: # Safety
                      sp = SubProcess(name="Controls", process_id=proc_obj.id)
                      db.add(sp)
                      db.commit()
                 # Insert mapping direct (ignore if exists which it shouldn't)
                 try:
                     db.execute(process_control_mapping.insert().values(subprocess_id=sp.id, control_id=control.id))
                 except: 
                     pass
            
            # B. Create Universal Intents (The Granular Requirements)
            for _, row in group_df.iterrows():
                 intent_ref_id = str(row.get('Intent_id'))
                 
                 # Upsert UniversalIntent
                 ui = db.query(UniversalIntent).filter(UniversalIntent.intent_id == intent_ref_id).first()
                 if not ui:
                      ui = UniversalIntent(
                          intent_id=intent_ref_id,
                          description=str(row.get('Intent_statement', '')),
                          category=dominant_process_name,
                          status=IntentStatus.PENDING
                      )
                      db.add(ui)
                      db.commit()
                      db.refresh(ui)
                      intents_upserted += 1
                 
                 # C. Link Intent to Framework Control
                 # Check exist
                 link = db.query(IntentFrameworkCrosswalk).filter(
                     IntentFrameworkCrosswalk.intent_id == ui.id,
                     IntentFrameworkCrosswalk.framework_id == ISO_FRAMEWORK_CODE,
                     IntentFrameworkCrosswalk.control_reference == control.id
                 ).first()
                 
                 if not link:
                     link = IntentFrameworkCrosswalk(
                         intent_id=ui.id,
                         framework_id=ISO_FRAMEWORK_CODE, # "ISO27001"
                         control_reference=control.control_id # "A.5.1"
                     )
                     db.add(link)
                     links_created += 1
        
        db.commit()
        print(f"[+] SUCCESS: Created {controls_created} Standard Controls.")
        print(f"[+] Upserted {intents_upserted} Intents.")
        print(f"[+] Created {links_created} Links.")

    except Exception as e:
        print(f"[!] Error: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    restructure_controls()
