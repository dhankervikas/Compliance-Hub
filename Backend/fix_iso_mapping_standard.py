from app.database import SessionLocal
from app.models.control import Control
import sys

def fix_iso_mappings_standard():
    db = SessionLocal()
    print("--- FIXING ISO 27001 TITLE MAPPINGS (MODERN STANDARD) ---")
    
    # Correct Mappings for Clauses (4-10) and Key Annex Controls
    mappings = {
        # CLAUSES (Context, Leadership, Planning, Support, Ops, Performance, Improvement)
        "4.1": "Determine Context & Stakeholders",
        "4.2": "Identify Interested Parties",
        "4.3": "Define Scope of ISMS",
        "4.4": "Maintain ISMS Processes",
        "5.1": "Demonstrate Leadership & Commitment",
        "5.2": "Establish Information Security Policy",
        "5.3": "Assign Roles & Responsibilities",
        "6.1": "Address Risks & Opportunities",
        "6.2": "Set Security Objectives",
        "6.3": "Plan Changes",
        "7.1": "Provide Resources",
        "7.2": "Ensure Competence",
        "7.3": "Facilitate Awareness",
        "7.4": "Manage Communications",
        "7.5": "Control Documented Information",
        "8.1": "Plan & Control Operations",
        "8.2": "Assess Information Security Risks",
        "8.3": "Treat Information Security Risks",
        "9.1": "Monitor, Measure, Analyze & Evaluate",
        "9.2": "Conduct Internal Audit",
        "9.3": "Conduct Management Review",
        "10.1": "Correct Nonconformities",
        "10.2": "Continual Improvement",

        # ANNEX A (Using 2022 Numbering A.5.x, A.6.x, A.7.x, A.8.x)
        # Ensure A.5.1 is POLICY
        "A.5.1": "Policies for Information Security",
        "A.5.2": "Information Security Roles & Responsibilities",
        "A.5.3": "Segregation of Duties",
        "A.5.4": "Management Responsibilities",
        "A.5.5": "Contact with Authorities",
        "A.5.6": "Contact with Special Interest Groups",
        "A.5.7": "Threat Intelligence",
        "A.5.8": "Information Security in Project Management",
        "A.5.9": "Inventory of Information and Other Associated Assets",
        "A.5.10": "Acceptable Use of Information and Other Associated Assets",
    }

    # Dynamic Framework Lookup
    from app.models.framework import Framework
    fw = db.query(Framework).filter(Framework.code == "ISO27001").first()
    if not fw:
        print("ERROR: Could not find ISO27001 Framework!")
        return

    fw_id = fw.id
    print(f"Targeting Framework ID: {fw_id}")
    
    updated_count = 0
    
    for cid, correct_title in mappings.items():
        control = db.query(Control).filter(
            Control.framework_id == fw_id, 
            Control.control_id == cid
        ).first()
        
        if control:
            old_title = control.title
            if old_title != correct_title:
                print(f"Updating {cid}:")
                # print(f"   OLD: {old_title}")
                print(f"   NEW: {correct_title}")
                control.title = correct_title
                control.actionable_title = correct_title 
                control.description = "ISO 27001 Standard Requirement"
                updated_count += 1
        else:
            # Try fuzzy match if exact ID fails (e.g. 5.1 vs A.5.1 db side)
            pass

    db.commit()
    print(f"--- UPDATE COMPLETE. {updated_count} Controls Fixed. ---")
    db.close()

if __name__ == "__main__":
    fix_iso_mappings_standard()
