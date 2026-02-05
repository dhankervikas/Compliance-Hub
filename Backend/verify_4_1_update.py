from app.database import SessionLocal
from app.models.control import Control
import json

def verify_update():
    db = SessionLocal()
    # Find 4.1 (ID 4753 or control_id "4.1")
    c = db.query(Control).filter(Control.control_id == "4.1").first()
    if c:
        print(f"Control: {c.control_id} - {c.title}")
        print(f"Explanation: {c.ai_explanation}")
        if c.ai_requirements_json:
            print(f"JSON Requirements: {c.ai_requirements_json[:200]}...") 
        else:
            print("JSON Requirements: (Pending Generation)")
    else:
        print("Control 4.1 not found.")
    db.close()

if __name__ == "__main__":
    verify_update()
