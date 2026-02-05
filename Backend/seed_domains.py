from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.control import Control, AutomationStatus

def seed_process_domains():
    db = SessionLocal()
    try:
        controls = db.query(Control).all()
        print(f"Found {len(controls)} controls. Tagging domains...")
        
        updates = 0
        for control in controls:
            domain = "General"
            
            # Simple heuristic for ISO 27001 Annex A controls
            if "A.5" in control.control_id:
                domain = "Information Security Policies"
            elif "A.6" in control.control_id or "A.7" in control.control_id:
                domain = "Organization of Information Security"
            elif "A.8" in control.control_id:
                domain = "Asset Management"
            elif "A.9" in control.control_id:
                domain = "Access Management"
            elif "A.10" in control.control_id:
                domain = "Cryptography"
            elif "A.11" in control.control_id:
                domain = "Physical & Environmental Security"
            elif "A.12" in control.control_id:
                domain = "Operations Security"
            elif "A.13" in control.control_id:
                domain = "Communications Security"
            elif "A.14" in control.control_id:
                domain = "System Acquisition, Development and Maintenance"
            elif "A.15" in control.control_id:
                domain = "Supplier Relationships"
            elif "A.16" in control.control_id:
                domain = "Incident Management"
            elif "A.17" in control.control_id:
                domain = "Business Continuity Management"
            elif "A.18" in control.control_id:
                domain = "Compliance"
            
            # Simulate some automated status
            if domain in ["Access Management", "Operations Security"]:
                control.automation_status = AutomationStatus.HYBRID
            else:
                control.automation_status = AutomationStatus.MANUAL
                
            control.domain = domain
            updates += 1
            print(f"Tagged {control.control_id} -> {domain}")
            
        db.commit()
        print(f"Successfully updated {updates} controls.")
        
    except Exception as e:
        print(f"Error seeding domains: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_process_domains()
