from app.database import SessionLocal, engine, Base
from app.models.person import Person
from app.models.control import Control
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def patch_controls():
    db = SessionLocal()
    try:
        # A.8.12 Data Leakage Prevention
        a812 = db.query(Control).filter(Control.control_id == "A.8.12").first()
        if a812:
            logger.info("Found A.8.12. Updating Requirements...")
            requirements = [
                {
                    "name": "DLP Technical Configuration Rules",
                    "type": "Technical Log",
                    "desc": "Screenshot/Export of active DLP rules blocking sensitive data exfiltration.",
                    "automation_potential": True,
                    "audit_guidance": "Good: JSON export of rules. Bad: Generic policy."
                },
                {
                    "name": "Data Classification Schema",
                    "type": "Policy",
                    "desc": "Document defining sensitive data types (PII, PHI).",
                    "automation_potential": False,
                    "audit_guidance": "Good: Specific categories. Bad: 'Confidential' label only."
                },
                {
                    "name": "DLP Incident Remediation Logs",
                    "type": "Log",
                    "desc": "Logs showing blocked attempts and security team response.",
                    "automation_potential": True,
                    "audit_guidance": "Good: Ticket ID and resolution. Bad: Empty log."
                }
            ]
            a812.ai_requirements_json = json.dumps(requirements)
            a812.ai_explanation = "Prevent unauthorized disclosure of information."
            db.add(a812)
            logger.info("A.8.12 Updated.")

        # A.5.15 Access Control (or title match)
        a515 = db.query(Control).filter(Control.control_id == "A.5.15").first()
        if a515:
            logger.info("Found A.5.15. Updating Requirements...")
            reqs_515 = [
                {
                    "name": "Access Control Policy",
                    "type": "Policy",
                    "desc": "Rules for user registration and deregistration.",
                    "automation_potential": False
                },
                {
                    "name": "User Access Rights Review (Quarterly)",
                    "type": "Review",
                    "desc": "Evidence of access recertification.",
                    "automation_potential": True
                }
            ]
            a515.ai_requirements_json = json.dumps(reqs_515)
            db.add(a515)
            logger.info("A.5.15 Updated.")

        db.commit()
        logger.info("Database Commit Successful.")
    except Exception as e:
        logger.error(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    patch_controls()
