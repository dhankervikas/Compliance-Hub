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

# Constants
MASTER_FILE = r"C:\Projects\Compliance_Product\Backend\MASTER_ISO27001_INTENTS.csv"

# Official ISO 27001:2022 Standard Names
ISO_STANDARDS = {
    # Clause 4 (Context)
    "4.1": "Understanding the organization and its context",
    "4.2": "Understanding the needs and expectations of interested parties",
    "4.3": "Determining the scope of the information security management system",
    "4.4": "Information security management system",
    # Clause 5 (Leadership)
    "5.1": "Leadership and commitment",
    "5.2": "Policy",
    "5.3": "Organizational roles, responsibilities and authorities",
    # Clause 6 (Planning)
    "6.1": "Actions to address risks and opportunities",  # Catch-all
    "6.1.1": "General",
    "6.1.2": "Information security risk assessment",
    "6.1.3": "Information security risk treatment",
    "6.2": "Information security objectives and planning to achieve them",
    "6.3": "Planning of changes",
    # Clause 7 (Support)
    "7.1": "Resources",
    "7.2": "Competence",
    "7.3": "Awareness",
    "7.4": "Communication",
    "7.5": "Documented information", # Catch-all
    "7.5.1": "General",
    "7.5.2": "Creating and updating",
    "7.5.3": "Control of documented information",
    # Clause 8 (Operation)
    "8.1": "Operational planning and control",
    "8.2": "Information security risk assessment",
    "8.3": "Information security risk treatment",
    # Clause 9 (Performance)
    "9.1": "Monitoring, measurement, analysis and evaluation",
    "9.2": "Internal audit", # Catch-all
    "9.2.1": "General",
    "9.2.2": "Internal audit programme",
    "9.3": "Management review", # Catch-all
    "9.3.1": "General",
    "9.3.2": "Management review inputs",
    "9.3.3": "Management review results",
    # Clause 10 (Improvement)
    "10.1": "Continual improvement",
    "10.2": "Nonconformity and corrective action",
    
    # Annex A - 5 (Organizational)
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
    
    # Annex A - 6 (People)
    "A.6.1": "Screening",
    "A.6.2": "Terms and conditions of employment",
    "A.6.3": "Information security awareness, education and training",
    "A.6.4": "Disciplinary process",
    "A.6.5": "Responsibilities after termination or change of employment",
    "A.6.6": "Confidentiality or non-disclosure agreements",
    "A.6.7": "Remote working",
    "A.6.8": "Information security event reporting",
    
    # Annex A - 7 (Physical)
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
    
    # Annex A - 8 (Technological)
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

def fix_titles():
    print(f"[-] Starting FIX_STANDARD_TITLES...")
    
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 1. Ingest Master File just for Intent -> Clause mapping
        print(f"[-] Reading Map from CSV: {MASTER_FILE}")
        df = pd.read_csv(MASTER_FILE)
        
        # Create map: Intent_ID -> Clause (e.g., INT-04-01 -> 4.1)
        # Note: If intent appears multiple times, use first valid non-nan
        intent_map = {}
        for index, row in df.iterrows():
            intent_id = str(row.get('Intent_id', index))
            clause = str(row.get('Clause_or_control', '')).strip()
            
            # Normalize Clause: "A.5.1"
            if not clause or clause == 'nan':
                continue
                
            if intent_id not in intent_map:
                intent_map[intent_id] = clause
                
        print(f"[-] Mapped {len(intent_map)} intents to clauses.")
        
        # 2. Update Controls
        controls = db.query(Control).all()
        updated = 0
        
        for c in controls:
            # Get Clause
            clause = intent_map.get(c.control_id)
            if not clause:
                continue
                
            # Get Standard Name
            std_name = ISO_STANDARDS.get(clause)
            
            # Fallback for "A.5.1" vs "5.1" mismatch?
            if not std_name and not clause.startswith("A.") and f"A.{clause}" in ISO_STANDARDS:
                 std_name = ISO_STANDARDS[f"A.{clause}"]
            
            if std_name:
                c.description = f"{clause} {std_name}" # e.g., "A.5.1 Policies for information security"
                # Keep Title as the Long Intent Statement (already set)
                db.add(c)
                updated += 1
            else:
                 # If no standard name found, keep existing or mark?
                 pass
            
        db.commit()
        print(f"[+] SUCCESS: Applied Standard Names to {updated} controls.")
        
    except Exception as e:
        print(f"[!] Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_titles()
