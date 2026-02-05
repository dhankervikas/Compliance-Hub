from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.framework import Framework
from app.models.control import Control
from app.models.policy import Policy
import json
import datetime

# --- CONTROL DATA (Source of Truth) ---
ISO_42001_CONTROLS = [
    # --- CLAUSE 4: CONTEXT ---
    { "control_id": "ISO42001-4.1", "title": "4.1 Understanding organization", "description": "Determine external and internal issues relevant to the AIMS.", "category": "Governance" },
    { "control_id": "ISO42001-4.2", "title": "4.2 Interested Parties", "description": "Determine requirements of interested parties relevant to the AIMS.", "category": "Governance" },
    { "control_id": "ISO42001-4.3", "title": "4.3 Scope of AIMS", "description": "Determine and document the scope of the AIMS.", "category": "Governance" },
    { "control_id": "ISO42001-4.4", "title": "4.4 AIMS Processes", "description": "Establish, implement, maintain, and continually improve the AIMS.", "category": "Governance" },

    # --- CLAUSE 5: LEADERSHIP ---
    { "control_id": "ISO42001-5.1", "title": "5.1 Leadership & Commitment", "description": "Top management demonstrates leadership and commitment to the AIMS.", "category": "Governance" },
    { "control_id": "ISO42001-5.2", "title": "5.2 AI Policy", "description": "Establish and communicate the AI policy.", "category": "Governance" },
    { "control_id": "ISO42001-5.3", "title": "5.3 Roles & Responsibilities", "description": "Assign and communicate organizational roles, responsibilities, and authorities for AI.", "category": "Governance" },

    # --- CLAUSE 6: PLANNING ---
    { "control_id": "ISO42001-6.1.1", "title": "6.1.1 General Actions", "description": "Plan actions to address risks and opportunities related to AI.", "category": "Governance" },
    { "control_id": "ISO42001-6.1.2", "title": "6.1.2 AI Risk Assessment", "description": "Define and apply an AI risk assessment process.", "category": "Governance" },
    { "control_id": "ISO42001-6.1.3", "title": "6.1.3 AI Risk Treatment", "description": "Define and apply an AI risk treatment process.", "category": "Governance" },
    { "control_id": "ISO42001-6.1.4", "title": "6.1.4 AI System Impact Assessment", "description": "Assess the impact of AI systems on individuals and society.", "category": "Governance" },
    { "control_id": "ISO42001-6.2", "title": "6.2 AI Objectives", "description": "Establish AI objectives and plans to achieve them.", "category": "Governance" },
    { "control_id": "ISO42001-6.3", "title": "6.3 Planning of Changes", "description": "Changes to the AIMS are carried out in a planned manner.", "category": "Governance" },

    # --- CLAUSE 7: SUPPORT ---
    { "control_id": "ISO42001-7.1", "title": "7.1 Resources", "description": "Provide resources needed for the AIMS, including data, computing, and tools.", "category": "Governance" },
    { "control_id": "ISO42001-7.2", "title": "7.2 Competence", "description": "Ensure necessary competence of persons doing work under the organization's control regarding AI.", "category": "Governance" },
    { "control_id": "ISO42001-7.3", "title": "7.3 Awareness", "description": "Ensure persons are aware of the AI policy and their contribution to effectiveness.", "category": "Governance" },
    { "control_id": "ISO42001-7.4", "title": "7.4 Communication", "description": "Determine internal and external communications relevant to the AIMS.", "category": "Governance" },
    { "control_id": "ISO42001-7.5.1", "title": "7.5.1 General", "description": "AIMS shall include documented information required by the standard and determined by the organization.", "category": "Governance" },
    { "control_id": "ISO42001-7.5.2", "title": "7.5.2 Creating and updating", "description": "Ensure appropriate identification, format, and review when creating and updating documented information.", "category": "Governance" },
    { "control_id": "ISO42001-7.5.3", "title": "7.5.3 Control of documented information", "description": "Documented information shall be controlled to ensure availability and suitability.", "category": "Governance" },

    # --- CLAUSE 8: OPERATION ---
    { "control_id": "ISO42001-8.1", "title": "8.1 Operational Planning", "description": "Plan, implement, and control processes needed to meet AI requirements.", "category": "Technical" },
    { "control_id": "ISO42001-8.2", "title": "8.2 AI Risk Assessment", "description": "Perform AI risk assessments at planned intervals.", "category": "Governance" },
    { "control_id": "ISO42001-8.3", "title": "8.3 AI Risk Treatment", "description": "Implement the AI risk treatment plan.", "category": "Governance" },
    { "control_id": "ISO42001-8.4", "title": "8.4 AI System Impact Assessment", "description": "Perform AI system impact assessments.", "category": "Governance" },

    # --- CLAUSE 9: PERFORMANCE ---
    { "control_id": "ISO42001-9.1", "title": "9.1 Monitoring & Measurement", "description": "Evaluate the performance and effectiveness of the AIMS.", "category": "Governance" },
    { "control_id": "ISO42001-9.2.1", "title": "9.2.1 General", "description": "Conduct internal audits at planned intervals.", "category": "Governance" },
    { "control_id": "ISO42001-9.2.2", "title": "9.2.2 Internal Audit Programme", "description": "Plan, establish, implement, and maintain an audit programme.", "category": "Governance" },
    { "control_id": "ISO42001-9.3.1", "title": "9.3.1 General", "description": "Top management shall review the AIMS at planned intervals.", "category": "Governance" },
    { "control_id": "ISO42001-9.3.2", "title": "9.3.2 Management Review Inputs", "description": "The management review shall include consideration of status of actions, changes, and performance.", "category": "Governance" },
    { "control_id": "ISO42001-9.3.3", "title": "9.3.3 Management Review Results", "description": "The outputs of the management review shall include decisions related to improvement.", "category": "Governance" },

    # --- CLAUSE 10: IMPROVEMENT ---
    { "control_id": "ISO42001-10.1", "title": "10.1 Continual Improvement", "description": "Continually improve the suitability, adequacy, and effectiveness of the AIMS.", "category": "Governance" },
    { "control_id": "ISO42001-10.2", "title": "10.2 Nonconformity", "description": "React to nonconformities and take action to control and correct them.", "category": "Governance" },

    # --- ANNEX A CONTROLS (Normative) ---
    # A.2 Policies related to AI
    { "control_id": "ISO42001-A.2.2", "title": "A.2.2 AI policy", "description": "An AI policy involves a document or a set of documents that outline an organization's specific requirements principles and guidelines.", "category": "Governance" },
    { "control_id": "ISO42001-A.2.3", "title": "A.2.3 Alignment with other organizational policies", "description": "AI policies should align with other organizational policies to ensure consistency.", "category": "Governance" },
    { "control_id": "ISO42001-A.2.4", "title": "A.2.4 Review of the AI policy", "description": "The AI policy should be reviewed at planned intervals or if significant changes occur.", "category": "Governance" },

    # A.3 Internal Organization
    { "control_id": "ISO42001-A.3.2", "title": "A.3.2 Roles and Responsibilities", "description": "Roles and responsibilities for AI systems should be defined and allocated.", "category": "Governance" },
    { "control_id": "ISO42001-A.3.3", "title": "A.3.3 Reporting", "description": "Reporting of AI-related issues and concerns.", "category": "Governance" },

    # A.4 Resources for AI systems
    { "control_id": "ISO42001-A.4.2", "title": "A.4.2 Data Resources", "description": "Resources for data management and quality.", "category": "Technical" },
    { "control_id": "ISO42001-A.4.3", "title": "A.4.3 Tooling", "description": "Provision of adequate tools and computing resources for AI.", "category": "Technical" },
    { "control_id": "ISO42001-A.4.4", "title": "A.4.4 System and Computing Resources", "description": "Allocation of sufficient computing and system resources.", "category": "Technical" },
    { "control_id": "ISO42001-A.4.5", "title": "A.4.5 Human Resources", "description": "Competence and training of personnel involved in AI.", "category": "Governance" },
    { "control_id": "ISO42001-A.4.6", "title": "A.4.6 External Resources", "description": "Management of external resources used in AI systems.", "category": "Governance" },
    
    # A.5 Impact Assessment
    { "control_id": "ISO42001-A.5.2", "title": "A.5.2 Impact Assessment Process", "description": "A defined process for assessing the impact of AI systems on individuals and society.", "category": "Governance" },
    { "control_id": "ISO42001-A.5.3", "title": "A.5.3 Assessment Documentation", "description": "Documentation of impact assessment results.", "category": "Governance" },
    { "control_id": "ISO42001-A.5.4", "title": "A.5.4 Impact Re-assessment", "description": "Re-assessing impacts when changes occur.", "category": "Governance" },
    { "control_id": "ISO42001-A.5.5", "title": "A.5.5 Mitigation of Impacts", "description": "Implementing measures to mitigate identified adverse impacts.", "category": "Governance" },

    # A.6 AI System Life Cycle
    # A.6.1 Concept and Definition
    { "control_id": "ISO42001-A.6.1.2", "title": "A.6.1.2 AI System Definition", "description": "Definition of AI system objectives and scope.", "category": "Technical" },
    { "control_id": "ISO42001-A.6.1.3", "title": "A.6.1.3 AI System Requirements", "description": "Documenting requirements for the AI system.", "category": "Technical" },

    # A.6.2 Design and Development
    { "control_id": "ISO42001-A.6.2.2", "title": "A.6.2.2 Design and Development", "description": "Responsible design and development process.", "category": "Technical" },
    { "control_id": "ISO42001-A.6.2.3", "title": "A.6.2.3 Verification and Validation", "description": "V&V of AI systems against requirements.", "category": "Technical" },
    { "control_id": "ISO42001-A.6.2.4", "title": "A.6.2.4 Deployment", "description": "Responsible deployment of AI systems.", "category": "Technical" },
    { "control_id": "ISO42001-A.6.2.5", "title": "A.6.2.5 Operation and Monitoring", "description": "Monitoring and operation of AI systems.", "category": "Technical" },
    { "control_id": "ISO42001-A.6.2.6", "title": "A.6.2.6 Technical Vulnerability Management", "description": "Managing technical vulnerabilities in AI systems.", "category": "Technical" },
    { "control_id": "ISO42001-A.6.2.7", "title": "A.6.2.7 AI System Retirement", "description": "Decommissioning and retirement of AI systems.", "category": "Technical" },
    { "control_id": "ISO42001-A.6.2.8", "title": "A.6.2.8 Event Logging", "description": "Logging of events relevant to the AI system.", "category": "Technical" },
    
    # A.7 Data for AI systems
    { "control_id": "ISO42001-A.7.2", "title": "A.7.2 Data Acquisition", "description": "Responsible acquisition and collection of data for AI.", "category": "Governance" },
    { "control_id": "ISO42001-A.7.3", "title": "A.7.3 Data Quality", "description": "Measures to ensure data quality and suitability.", "category": "Technical" },
    { "control_id": "ISO42001-A.7.4", "title": "A.7.4 Data Provenance", "description": "Tracking of data provenance and lineage.", "category": "Technical" },
    { "control_id": "ISO42001-A.7.5", "title": "A.7.5 Data Preparation", "description": "Responsible data cleaning, labeling, and preparation.", "category": "Technical" },
    { "control_id": "ISO42001-A.7.6", "title": "A.7.6 Data Protection", "description": "Protection of data used in AI systems.", "category": "Technical" },

    # A.8 Information for Interested Parties
    { "control_id": "ISO42001-A.8.2", "title": "A.8.2 External Communication", "description": "Providing information to users and other stakeholders about AI systems.", "category": "Governance" },
    { "control_id": "ISO42001-A.8.3", "title": "A.8.3 Transparency", "description": "Transparency regarding the use and nature of AI systems.", "category": "Governance" },
    { "control_id": "ISO42001-A.8.4", "title": "A.8.4 Reporting", "description": "Reporting to interested parties.", "category": "Governance" },
    { "control_id": "ISO42001-A.8.5", "title": "A.8.5 Notification", "description": "Notification of adverse events or incidents.", "category": "Governance" },

    # A.9 Use of AI Systems
    { "control_id": "ISO42001-A.9.2", "title": "A.9.2 Responsible Use", "description": "Guidelines for the responsible use of AI systems.", "category": "Governance" },
    { "control_id": "ISO42001-A.9.3", "title": "A.9.3 Human Oversight", "description": "Human oversight of AI systems.", "category": "Governance" },
    { "control_id": "ISO42001-A.9.4", "title": "A.9.4 Intended Use", "description": "Ensuring AI systems are used for intended purposes.", "category": "Governance" },

    # A.10 Third-Party Relationships
    { "control_id": "ISO42001-A.10.2", "title": "A.10.2 Supplier Management", "description": "Management of AI-related suppliers and partners.", "category": "Governance" },
    { "control_id": "ISO42001-A.10.3", "title": "A.10.3 Customer Management", "description": "Management of AI-related customer relationships.", "category": "Governance" },
    { "control_id": "ISO42001-A.10.4", "title": "A.10.4 Third-Party Risk Management", "description": "Managing risks associated with third-party AI systems.", "category": "Governance" }
]

# --- POLICY DATA ---
AI_POLICIES = [
    {
        "name": "Artificial Intelligence Policy",
        "description": "High-level policy governing the development, deployment, and use of AI systems.",
        "controls": ["ISO42001-A.2.2", "ISO42001-A.2.3", "ISO42001-5.2"],
        "content_template": """# Artificial Intelligence (AI) Policy

**Version:** 1.0 (Template)
**Date:** {date}
**Owner:** {policy_owner}

---

## 1. Purpose
The purpose of this AI Policy is to ensure that all Artificial Intelligence (AI) systems developed, deployed, or used by {company_name} are trustworthy, ethical, secure, and compliant with ISO/IEC 42001:2023.

## 2. Scope
This policy applies to all AI systems and machine learning models within {company_name}'s environment, including third-party AI tools.

## 3. Policy Statements

### 3.1 Responsible AI Principles
{company_name} commits to the following principles:
- **Fairness:** Preventing bias in AI outcomes.
- **Transparency:** Ensuring stakeholders understand AI decisions (Explainability).
- **Safety & Security:** Protecting AI systems from adversarial attacks.
- **Accountability:** Assigning clear ownership for AI system behavior.

### 3.2 AI System Lifecycle
All AI systems must go through a defined lifecycle process including:
- Impact Assessment prior to development.
- Data quality verification.
- Model validation and testing.
- Continuous monitoring post-deployment.

### 3.3 Risk Management
Risk assessments specific to AI (e.g., unintended model bias, drift) must be conducted at least annually.

## 4. Compliance Mapping
| Control | Requirement |
| :--- | :--- |
| ISO 42001 A.2.2 | AI Policy |
| ISO 42001 5.2 | AI Policy Requirement |
"""
    },
    {
        "name": "AI System Impact Assessment Procedure",
        "description": "Procedure for assessing the impact of AI systems on individuals and society.",
        "controls": ["ISO42001-6.1.4", "ISO42001-A.5.2", "ISO42001-A.5.3"],
        "content_template": """# AI System Impact Assessment Procedure

**Version:** 1.0 (Template)

## 1. Purpose
To define the methodology for assessing the potential impact of AI systems.

## 2. Assessment Criteria
- Nature of decision making (High/Low stakes).
- Impact on fundamental rights.
- Potential for physical or psychological harm.

## 3. Procedure
1. Identify the AI System purpose.
2. Evaluate potential adverse impacts.
3. Classify risk level (Low, Medium, High).
4. Define mitigation strategies.
"""
    },
    {
        "name": "AI Data Governance Policy",
        "description": "Rules for acquiring, cleaning, and managing data used in AI training and inference.",
        "controls": ["ISO42001-A.7.2", "ISO42001-A.7.3", "ISO42001-A.7.4"],
        "content_template": """# AI Data Governance Policy

**Version:** 1.0 (Template)

## 1. Data Acquisition
Data must be obtained legally and ethically.

## 2. Data Quality
Training data must be representative, free from material bias, and relevant to the problem.

## 3. Data Lineage
All data sets used for model training must be version-controlled and traceable.
"""
    }
]

def seed_iso42001():
    db = SessionLocal()
    print("Seeding ISO 42001:2023 Framework & Controls...")

    try:
        # 1. Ensure Framework Exists
        fw_code = "ISO42001"
        fw_name = "ISO 42001:2023"
        
        fw = db.query(Framework).filter(Framework.code == fw_code).first()
        if not fw:
            print(f"Creating Framework: {fw_name}")
            fw = Framework(
                name=fw_name,
                code=fw_code,
                description="Artificial Intelligence Management System",
                version="2023"
            )
            db.add(fw)
            db.commit()
            db.refresh(fw)
        else:
            print(f"Framework {fw_name} exists (ID: {fw.id})")

        # 2. Seed Controls (Idempotent by Delete First)
        print(f"Seeding {len(ISO_42001_CONTROLS)} Controls...")
        
        # DELETE existing controls for this framework to ensure clean state and remove bad IDs
        db.query(Control).filter(Control.framework_id == fw.id).delete()
        db.commit()

        count = 0
        for c_data in ISO_42001_CONTROLS:
            # Check if exists
            control = db.query(Control).filter(Control.control_id == c_data["control_id"]).first()
            if not control:
                new_c = Control(
                    framework_id=fw.id,
                    control_id=c_data["control_id"],
                    title=c_data["title"],
                    description=c_data["description"],
                    category=c_data["category"],
                    status="not_started"
                )
                db.add(new_c)
                count += 1
            else:
                # Update if needed
                control.title = c_data["title"]
                control.description = c_data["description"]
                control.category = c_data["category"]
                control.framework_id = fw.id # Ensure link
        
        db.commit()
        print(f"Added {count} new controls.")

        # 3. Seed Policies
        print("Seeding AI Policies...")
        p_count = 0
        for p_data in AI_POLICIES:
            name = p_data["name"]
            existing = db.query(Policy).filter(Policy.name == name).first()
            
            content = p_data["content_template"].replace("{date}", str(datetime.date.today()))
            
            if not existing:
                new_p = Policy(
                    name=name,
                    description=p_data["description"],
                    content=content,
                    version="1.0",
                    status="Draft",
                    is_template=True, # Mark as template/standard
                    linked_frameworks="ISO 42001:2023",
                    mapped_controls=json.dumps(p_data["controls"])
                )
                db.add(new_p)
                p_count += 1
            else:
                existing.linked_frameworks = "ISO 42001:2023"
                existing.mapped_controls = json.dumps(p_data["controls"])
        
        db.commit()
        print(f"Added {p_count} AI Policies.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding ISO 42001: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_iso42001()
