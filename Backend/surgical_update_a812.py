from app.database import SessionLocal
from app.models.control import Control
import json

def surgical_update():
    db = SessionLocal()
    control_id = "A.8.12"
    
    # 1. Fetch Control
    control = db.query(Control).filter(Control.control_id == control_id).first()
    
    if not control:
        print(f"ERROR: Control {control_id} not found!")
        return

    # 2. Define Surgical Requirements
    surgical_data = [
        {
            "name": "DLP Technical Policy & Configuration",
            "type": "Policy/Config",
            "desc": "Required per Master Intent Library",
            "automation_potential": True,
            "audit_guidance": "Good: Screenshots of active DLP rules (e.g., Purview, Zscaler) defining sensitive patterns (PII/PCI).\nBad: Generic policy document without technical rule evidence."
        },
        {
            "name": "Data Classification Schema",
            "type": "Standard",
            "desc": "Required per Master Intent Library",
            "automation_potential": False,
            "audit_guidance": "Good: Document defining tags (Public, Internal, Confidential, Restricted) and handling rules.\nBad: Ad-hoc labeling without formal definitions."
        },
        {
            "name": "Monitoring & Alerting Logs",
            "type": "Log",
            "desc": "Required per Master Intent Library",
            "automation_potential": True,
            "audit_guidance": "Good: System logs showing blocked unauthorized transfers or alerts.\nBad: Empty logs or logs unrelated to data exfiltration."
        },
        {
            "name": "Remediation Records",
            "type": "Record",
            "desc": "Required per Master Intent Library",
            "automation_potential": False,
            "audit_guidance": "Good: Ticket/Log showing investigation and closure of a DLP incident.\nBad: No evidence of response to alerts."
        }
    ]

    # 3. Apply Update
    print(f"Updating {control_id} with {len(surgical_data)} surgical requirements...")
    control.ai_requirements_json = json.dumps(surgical_data)
    control.ai_explanation = "This control requires technical measures to prevent unauthorized data exfiltration. Evidence must show active rules, classification, and incident handling."
    
    db.commit()
    print("SUCCESS: A.8.12 Surgical Update Applied.")

if __name__ == "__main__":
    surgical_update()
