"""
Script to fix ISMS clause data - replaces 'string' placeholders with proper values
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Control

# Proper ISMS clause data
ISMS_CLAUSES = {
    "4.1": {
        "title": "Understanding the organization and its context",
        "description": "The organization shall determine external and internal issues that are relevant to its purpose and that affect its ability to achieve the intended outcome(s) of its ISMS.",
        "category": "Context of the Organization",
    },
    "4.2": {
        "title": "Understanding the needs and expectations of interested parties",
        "description": "The organization shall determine interested parties that are relevant to the ISMS and their requirements relevant to information security.",
        "category": "Context of the Organization",
    },
    "4.3": {
        "title": "Determining the scope of the ISMS",
        "description": "The organization shall determine the boundaries and applicability of the ISMS to establish its scope.",
        "category": "Context of the Organization",
    },
    "4.4": {
        "title": "Information security management system",
        "description": "The organization shall establish, implement, maintain and continually improve an ISMS, including the processes needed and their interactions.",
        "category": "Context of the Organization",
    },
    "5.1": {
        "title": "Leadership and commitment",
        "description": "Top management shall demonstrate leadership and commitment with respect to the ISMS.",
        "category": "Leadership",
    },
    "5.2": {
        "title": "Policy",
        "description": "Top management shall establish an information security policy that is appropriate to the purpose of the organization.",
        "category": "Leadership",
    },
    "5.3": {
        "title": "Organizational roles, responsibilities and authorities",
        "description": "Top management shall ensure that responsibilities and authorities for roles relevant to information security are assigned and communicated.",
        "category": "Leadership",
    },
    "6.1.1": {
        "title": "General - Actions to address risks and opportunities",
        "description": "When planning for the ISMS, the organization shall consider the issues, requirements and determine risks and opportunities.",
        "category": "Planning",
    },
    "6.1.2": {
        "title": "Information security risk assessment",
        "description": "The organization shall define and apply an information security risk assessment process.",
        "category": "Planning",
    },
    "6.1.3": {
        "title": "Information security risk treatment",
        "description": "The organization shall define and apply an information security risk treatment process.",
        "category": "Planning",
    },
    "6.2": {
        "title": "Information security objectives and planning to achieve them",
        "description": "The organization shall establish information security objectives at relevant functions and levels.",
        "category": "Planning",
    },
    "6.3": {
        "title": "Planning of changes",
        "description": "When the organization determines the need for changes to the ISMS, the changes shall be carried out in a planned manner.",
        "category": "Planning",
    },
    "7.1": {
        "title": "Resources",
        "description": "The organization shall determine and provide the resources needed for the establishment, implementation, maintenance and continual improvement of the ISMS.",
        "category": "Support",
    },
    "7.2": {
        "title": "Competence",
        "description": "The organization shall determine the necessary competence of person(s) doing work under its control that affects its information security performance.",
        "category": "Support",
    },
    "7.3": {
        "title": "Awareness",
        "description": "Persons doing work under the organization's control shall be aware of the information security policy and their contribution to the effectiveness of the ISMS.",
        "category": "Support",
    },
    "7.4": {
        "title": "Communication",
        "description": "The organization shall determine the need for internal and external communications relevant to the ISMS.",
        "category": "Support",
    },
    "7.5.1": {
        "title": "General - Documented information",
        "description": "The organization's ISMS shall include documented information required by this document and determined as being necessary by the organization.",
        "category": "Support",
    },
    "7.5.2": {
        "title": "Creating and updating",
        "description": "When creating and updating documented information, the organization shall ensure appropriate identification, description, format and review.",
        "category": "Support",
    },
    "7.5.3": {
        "title": "Control of documented information",
        "description": "Documented information required by the ISMS shall be controlled to ensure it is available, suitable and adequately protected.",
        "category": "Support",
    },
    "8.1": {
        "title": "Operational planning and control",
        "description": "The organization shall plan, implement and control the processes needed to meet information security requirements.",
        "category": "Operation",
    },
    "8.2": {
        "title": "Information security risk assessment",
        "description": "The organization shall perform information security risk assessments at planned intervals.",
        "category": "Operation",
    },
    "8.3": {
        "title": "Information security risk treatment",
        "description": "The organization shall implement the information security risk treatment plan.",
        "category": "Operation",
    },
    "9.1": {
        "title": "Monitoring, measurement, analysis and evaluation",
        "description": "The organization shall evaluate the information security performance and the effectiveness of the ISMS.",
        "category": "Performance Evaluation",
    },
    "9.2": {
        "title": "Internal audit",
        "description": "The organization shall conduct internal audits at planned intervals to provide information on whether the ISMS conforms to requirements.",
        "category": "Performance Evaluation",
    },
    "9.3": {
        "title": "Management review",
        "description": "Top management shall review the organization's ISMS at planned intervals.",
        "category": "Performance Evaluation",
    },
    "10.1": {
        "title": "Continual improvement",
        "description": "The organization shall continually improve the suitability, adequacy and effectiveness of the ISMS.",
        "category": "Improvement",
    },
    "10.2": {
        "title": "Nonconformity and corrective action",
        "description": "When a nonconformity occurs, the organization shall react to the nonconformity, evaluate the need for action and implement any action needed.",
        "category": "Improvement",
    },
}

def fix_isms_clauses():
    """Fix all ISMS clause data"""
    db: Session = SessionLocal()
    
    try:
        print("Starting ISMS clauses fix...")
        print("-" * 50)
        
        updated_count = 0
        
        for control_id, data in ISMS_CLAUSES.items():
            # Find the control
            control = db.query(Control).filter(Control.control_id == control_id).first()
            
            if control:
                # Update fields
                control.title = data["title"]
                control.description = data["description"]
                control.category = data["category"]
                control.priority = "high"  # All ISMS clauses are high priority
                
                # Clear placeholder values
                if control.owner == "string":
                    control.owner = None
                if control.implementation_notes == "string":
                    control.implementation_notes = None
                
                updated_count += 1
                print(f"✓ Updated {control_id}: {data['title'][:50]}...")
            else:
                print(f"✗ Control {control_id} not found")
        
        # Commit all changes
        db.commit()
        
        print("-" * 50)
        print(f"✓ Successfully updated {updated_count} ISMS clauses!")
        print("\nChanges made:")
        print("- Fixed titles (removed 'string')")
        print("- Added proper descriptions")
        print("- Set appropriate categories")
        print("- Set priority to 'high'")
        print("- Cleared placeholder values")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_isms_clauses()