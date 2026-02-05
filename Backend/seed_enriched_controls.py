
import sys
import os
import requests
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# -----------------------------------------------------------------------------
# CONFIGURATION & DATA SOURCE
# -----------------------------------------------------------------------------
# Mapping ISO 42001 Annex A Sections (as per seedData.js) to User's 9 Business Domains
# My Seed Data: A.2, A.3, A.4, A.5, A.6, A.7, A.8, A.9, A.10
# User's Request (Approximate Mapping based on Titles):
# 1. AI Ethics & Governance -> A.2 (Policy), A.3 (Internal Org), A.9.2 (Oversight), A.10 (Third Party... wait, user put Third Party as #7)
# 2. Risk & Impact -> A.5 (Impact Assessment)
# 3. Data & Privacy -> A.7 (Data)
# 4. AI Engineering (MLOps) -> A.6 (Lifecycle)
# 5. Model Security -> (Not explicitly in my Annex A list, maybe covered in A.6 or A.4 tooling?) -> I will map A.6 here too or split if possible.
#    Actually, standard Annex A has minimal specific "Model Security" section, it's woven in.
#    I'll map A.6 to "4. AI Engineering (MLOps)" primarily.
# 6. Human-in-the-Loop -> A.8 (Information for Users / Transparency)
# 7. Third-Party / Supply Chain -> A.10 (Third Party)
# 8. People & Culture -> A.3 (Roles), A.4.3 (Human Resources)
# 9. Continuous Monitoring -> (Covered in Clause 9 Performance, but for Annex A... maybe A.6.5 Operation?)

DOMAIN_MAPPING = {
    # Clause 4-10 (Management System) -> Map to "AI Ethics & Governance" generally
    "4": "1. AI Ethics & Governance",
    "5": "1. AI Ethics & Governance",
    "6": "2. Risk & Impact",
    "7": "8. People & Culture", # 7.2 Competence, 7.3 Awareness
    "8": "4. AI Engineering (MLOps)", # 8.1 Ops Planning
    "9": "9. Continuous Monitoring", # Performance Eval
    "10": "1. AI Ethics & Governance", # Improvement

    # Annex A Mappings
    "A.2": "1. AI Ethics & Governance",
    "A.3": "1. AI Ethics & Governance", # Roles
    "A.4": "8. People & Culture", # Resources (HR, Tools). User put "People" as #8.
    "A.5": "2. Risk & Impact",
    "A.6": "4. AI Engineering (MLOps)",
    "A.7": "3. Data & Privacy",
    "A.8": "6. Human-in-the-Loop", # Transparency
    "A.9": "1. AI Ethics & Governance", # Responsible Use
    "A.10": "7. Third-Party / Supply Chain" 
}

# FULL DATASET (Copied from seedData.js)
ISO_42001_DATA = [
    # --- CLAUSE 4: CONTEXT ---
    { "control_id": "ISO42001-4.1", "title": "4.1 Understanding organization", "description": "Determine external and internal issues relevant to the AIMS.", "process": "Governance & Policy", "category": "Governance" },
    { "control_id": "ISO42001-4.2", "title": "4.2 Interested Parties", "description": "Determine requirements of interested parties relevant to the AIMS.", "process": "Governance & Policy", "category": "Governance" },
    { "control_id": "ISO42001-4.3", "title": "4.3 Scope of AIMS", "description": "Determine and document the scope of the AIMS.", "process": "Governance & Policy", "category": "Governance" },
    { "control_id": "ISO42001-4.4", "title": "4.4 AIMS Processes", "description": "Establish, implement, maintain, and continually improve the AIMS.", "process": "Governance & Policy", "category": "Governance" },

    # --- CLAUSE 5: LEADERSHIP ---
    { "control_id": "ISO42001-5.1", "title": "5.1 Leadership & Commitment", "description": "Top management demonstrates leadership and commitment to the AIMS.", "process": "Governance & Policy", "category": "Governance" },
    { "control_id": "ISO42001-5.2", "title": "5.2 AI Policy", "description": "Establish and communicate the AI policy.", "process": "Governance & Policy", "category": "Governance" },
    { "control_id": "ISO42001-5.3", "title": "5.3 Roles & Responsibilities", "description": "Assign and communicate organizational roles, responsibilities, and authorities for AI.", "process": "Governance & Policy", "category": "Governance" },

    # --- CLAUSE 6: PLANNING ---
    { "control_id": "ISO42001-6.1.1", "title": "6.1.1 General Actions", "description": "Plan actions to address risks and opportunities related to AI.", "process": "Risk Management", "category": "Governance" },
    { "control_id": "ISO42001-6.1.2", "title": "6.1.2 AI Risk Assessment", "description": "Define and apply an AI risk assessment process.", "process": "Risk Management", "category": "Governance" },
    { "control_id": "ISO42001-6.1.3", "title": "6.1.3 AI Risk Treatment", "description": "Define and apply an AI risk treatment process.", "process": "Risk Management", "category": "Governance" },
    { "control_id": "ISO42001-6.1.4", "title": "6.1.4 AI System Impact Assessment", "description": "Assess the impact of AI systems on individuals and society.", "process": "Risk Management", "category": "Governance" },
    { "control_id": "ISO42001-6.2", "title": "6.2 AI Objectives", "description": "Establish AI objectives and plans to achieve them.", "process": "Governance & Policy", "category": "Governance" },
    { "control_id": "ISO42001-6.3", "title": "6.3 Planning of Changes", "description": "Changes to the AIMS are carried out in a planned manner.", "process": "Governance & Policy", "category": "Governance" },

    # --- CLAUSE 7: SUPPORT ---
    { "control_id": "ISO42001-7.1", "title": "7.1 Resources", "description": "Provide resources needed for the AIMS, including data, computing, and tools.", "process": "Governance & Policy", "category": "Governance" },
    { "control_id": "ISO42001-7.2", "title": "7.2 Competence", "description": "Ensure necessary competence of persons doing work under the organization's control regarding AI.", "process": "HR Security", "category": "Governance" },
    { "control_id": "ISO42001-7.3", "title": "7.3 Awareness", "description": "Ensure persons are aware of the AI policy and their contribution to effectiveness.", "process": "HR Security", "category": "Governance" },
    { "control_id": "ISO42001-7.4", "title": "7.4 Communication", "description": "Determine internal and external communications relevant to the AIMS.", "process": "Governance & Policy", "category": "Governance" },
    { "control_id": "ISO42001-7.5", "title": "7.5 Documented Information", "description": "Include documented information required by the standard and the organization for AI.", "process": "Governance & Policy", "category": "Governance" },

    # --- CLAUSE 8: OPERATION ---
    { "control_id": "ISO42001-8.1", "title": "8.1 Operational Planning", "description": "Plan, implement, and control processes needed to meet AI requirements.", "process": "Risk Management", "category": "Technical" },
    { "control_id": "ISO42001-8.2", "title": "8.2 AI Risk Assessment", "description": "Perform AI risk assessments at planned intervals.", "process": "Risk Management", "category": "Governance" },
    { "control_id": "ISO42001-8.3", "title": "8.3 AI Risk Treatment", "description": "Implement the AI risk treatment plan.", "process": "Risk Management", "category": "Governance" },
    { "control_id": "ISO42001-8.4", "title": "8.4 AI System Impact Assessment", "description": "Perform AI system impact assessments.", "process": "Risk Management", "category": "Governance" },

    # --- CLAUSE 9: PERFORMANCE ---
    { "control_id": "ISO42001-9.1", "title": "9.1 Monitoring & Measurement", "description": "Evaluate the performance and effectiveness of the AIMS.", "process": "Performance Evaluation", "category": "Governance" },
    { "control_id": "ISO42001-9.2", "title": "9.2 Internal Audit", "description": "Conduct internal audits of AIMS at planned intervals.", "process": "Performance Evaluation", "category": "Governance" },
    { "control_id": "ISO42001-9.3", "title": "9.3 Management Review", "description": "Top management reviews the AIMS at planned intervals.", "process": "Performance Evaluation", "category": "Governance" },

    # --- CLAUSE 10: IMPROVEMENT ---
    { "control_id": "ISO42001-10.1", "title": "10.1 Continual Improvement", "description": "Continually improve the suitability, adequacy, and effectiveness of the AIMS.", "process": "Improvement", "category": "Governance" },
    { "control_id": "ISO42001-10.2", "title": "10.2 Nonconformity", "description": "React to nonconformities and take action to control and correct them.", "process": "Improvement", "category": "Governance" },

    # --- ANNEX A CONTROLS (Normative) ---
    # A.2 Policies
    { "control_id": "ISO42001-A.2.1", "title": "A.2.1 AI Policy Framework", "description": "Policies for the development and use of AI systems.", "process": "Governance & Policy", "category": "Governance" },
    { "control_id": "ISO42001-A.2.2", "title": "A.2.2 Alignment", "description": "Alignment of AI policies with other organizational policies.", "process": "Governance & Policy", "category": "Governance" },

    # A.3 Internal Organization
    { "control_id": "ISO42001-A.3.1", "title": "A.3.1 Roles and Responsibilities", "description": "Roles and responsibilities for AI systems defined and allocated.", "process": "Governance & Policy", "category": "Governance" },
    { "control_id": "ISO42001-A.3.2", "title": "A.3.2 Reporting", "description": "Reporting of AI-related issues and concerns.", "process": "Incident & Resilience", "category": "Governance" },

    # A.4 Resources
    { "control_id": "ISO42001-A.4.1", "title": "A.4.1 Data Resources", "description": "Resources for data management and quality.", "process": "Data Management", "category": "Technical" },
    { "control_id": "ISO42001-A.4.2", "title": "A.4.2 Tooling", "description": "Provision of adequate tools and computing resources for AI.", "process": "Ops & Infrastructure", "category": "Technical" },
    { "control_id": "ISO42001-A.4.3", "title": "A.4.3 Human Resources", "description": "Competence and training of personnel involved in AI.", "process": "HR Security", "category": "Governance" },

    # A.5 Impact Assessment
    { "control_id": "ISO42001-A.5.1", "title": "A.5.1 Impact Criteria", "description": "Criteria for assessing the impact of AI systems on individuals and society.", "process": "Risk Management", "category": "Governance" },
    { "control_id": "ISO42001-A.5.2", "title": "A.5.2 Documentation", "description": "Documentation of impact assessment results.", "process": "Risk Management", "category": "Governance" },

    # A.6 AI System Life Cycle
    { "control_id": "ISO42001-A.6.1", "title": "A.6.1 Concept and Definition", "description": "Definition of AI system objectives and scope.", "process": "SDLC (AI)", "category": "Technical" },
    { "control_id": "ISO42001-A.6.2", "title": "A.6.2 Design and Development", "description": "Responsible design and development of AI systems.", "process": "SDLC (AI)", "category": "Technical" },
    { "control_id": "ISO42001-A.6.3", "title": "A.6.3 Verification and Validation", "description": "Verification and validation of AI systems against requirements.", "process": "SDLC (AI)", "category": "Technical" },
    { "control_id": "ISO42001-A.6.4", "title": "A.6.4 Deployment", "description": "Responsible deployment of AI systems.", "process": "SDLC (AI)", "category": "Technical" },
    { "control_id": "ISO42001-A.6.5", "title": "A.6.5 Operation and Monitoring", "description": "Monitoring and operation of AI systems.", "process": "Ops & Infrastructure", "category": "Technical" },
    { "control_id": "ISO42001-A.6.6", "title": "A.6.6 Retirement", "description": "Decommissioning and retirement of AI systems.", "process": "SDLC (AI)", "category": "Technical" },

    # A.7 Data
    { "control_id": "ISO42001-A.7.1", "title": "A.7.1 Data Acquisition", "description": "Responsible acquisition and collection of data for AI.", "process": "Data Management", "category": "Governance" },
    { "control_id": "ISO42001-A.7.2", "title": "A.7.2 Data Quality", "description": "Measures to ensure data quality and suitability.", "process": "Data Management", "category": "Technical" },
    { "control_id": "ISO42001-A.7.3", "title": "A.7.3 Data Provenance", "description": "Tracking of data provenance and lineage.", "process": "Data Management", "category": "Technical" },
    { "control_id": "ISO42001-A.7.4", "title": "A.7.4 Data Preparation", "description": "Responsible data cleaning, labeling, and preparation.", "process": "Data Management", "category": "Technical" },

    # A.8 Information for Users
    { "control_id": "ISO42001-A.8.1", "title": "A.8.1 External Communication", "description": "Providing information to users and other stakeholders about AI systems.", "process": "Transparency", "category": "Governance" },
    { "control_id": "ISO42001-A.8.2", "title": "A.8.2 Transparency", "description": "Transparency regarding the use and nature of AI systems.", "process": "Transparency", "category": "Governance" },
    { "control_id": "ISO42001-A.8.3", "title": "A.8.3 Explainability", "description": "Provision of explainability for AI system outputs where appropriate.", "process": "Transparency", "category": "Technical" },

    # A.9 Use of AI Systems
    { "control_id": "ISO42001-A.9.1", "title": "A.9.1 Responsible Use", "description": "Guidelines for the responsible use of AI systems.", "process": "Ethics", "category": "Governance" },
    { "control_id": "ISO42001-A.9.2", "title": "A.9.2 Oversight", "description": "Human oversight of AI systems.", "process": "Governance & Policy", "category": "Governance" },

    # A.10 Third-Party Relationships
    { "control_id": "ISO42001-A.10.1", "title": "A.10.1 Supplier Management", "description": "Management of AI-related suppliers and partners.", "process": "Supplier Mgmt", "category": "Governance" },
    { "control_id": "ISO42001-A.10.2", "title": "A.10.2 Customer Management", "description": "Management of AI-related customer relationships.", "process": "Supplier Mgmt", "category": "Governance" }
]

NIST_DATA = [
     { "title": "ID.AM-1", "description": "Physical devices and systems within the organization are inventoried.", "category": "Identify" }
]

def derive_domain(control_id):
    """
    Auto-assigns one of the 9 Business Domains based on the ISO 42001 Control ID suffix.
    e.g. ISO42001-A.2.1 -> Parses 'A.2' -> DOMAIN_MAPPING['A.2'] -> '1. AI Ethics & Governance'
    """
    # 1. Check for Annex A "A.X"
    if "A." in control_id:
        parts = control_id.split("A.")
        if len(parts) > 1:
            section = "A." + parts[1].split(".")[0] # Get A.2, A.3 etc
            return DOMAIN_MAPPING.get(section, "General Deployment")
    
    # 2. Check for Clause "ISO42001-X"
    parts = control_id.split("-")
    if len(parts) > 1:
        clause_part = parts[1]
        clause_num = clause_part.split(".")[0]
        return DOMAIN_MAPPING.get(clause_num, "General Deployment")
        
    return "General Deployment"

# -----------------------------------------------------------------------------
# SEEDING LOGIC
# -----------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Adjust path to DB relative to Backend/ folder if script is running from root or Backend
if os.path.exists(os.path.join(BASE_DIR, "sql_app.db")):
    DB_PATH = f"sqlite:///{os.path.join(BASE_DIR, 'sql_app.db')}"
else:
    DB_PATH = f"sqlite:///{os.path.join(BASE_DIR, '..', 'sql_app.db')}" # Try one up if in backend/app

engine = create_engine(DB_PATH)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed():
    session = SessionLocal()
    from app.models.control import Control, ControlStatus
    
    TENANT_SLUG = "testtest"
    ISO_ID = 6
    NIST_ID = 5
    
    print(f"--- Seeding Enriched Controls for {TENANT_SLUG} ---")
    
    try:
        # 1. Clean existing ISO 42001 & NIST for this tenant (Reset)
        print("Cleaning existing controls...")
        session.query(Control).filter(
            Control.tenant_id == TENANT_SLUG, 
            Control.framework_id.in_([ISO_ID, NIST_ID])
        ).delete(synchronize_session=False)
        
        # 2. Seed ISO 42001 with Domains
        print(f"Seeding {len(ISO_42001_DATA)} ISO 42001 Controls...")
        new_controls = []
        for c in ISO_42001_DATA:
            business_domain = derive_domain(c['control_id'])
            
            nc = Control(
                control_id=c['control_id'],
                title=c['title'],
                description=c['description'],
                framework_id=ISO_ID,
                tenant_id=TENANT_SLUG,
                status=ControlStatus.NOT_STARTED,
                category=c['category'],
                domain=business_domain, # Storing Business Domain here!
                is_applicable=True
            )
            new_controls.append(nc)
            
        session.add_all(new_controls)
        
        # 3. Seed NIST
        print(f"Seeding {len(NIST_DATA)} NIST Controls...")
        nist_controls = []
        for c in NIST_DATA:
            nc = Control(
                control_id=c['title'], # NIST uses title as ID in seedData?
                title=c['title'],
                description=c['description'],
                framework_id=NIST_ID,
                tenant_id=TENANT_SLUG,
                status=ControlStatus.NOT_STARTED,
                category=c['category'],
                domain="NIST Core",
                is_applicable=True
            )
            nist_controls.append(nc)
            
        session.add_all(nist_controls)
        
        session.commit()
        print("Seeding Complete. Enriched with Domains.")
        
    except Exception as e:
        session.rollback()
        print(f"Error seeding: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    seed()
