from app.database import SessionLocal
from app.models.control import Control
from sqlalchemy import func

def check_duplicates():
    db = SessionLocal()
    print("--- CHECKING FOR DUPLICATE 4.1 CONTROLS ---")
    
    controls = db.query(Control).filter(Control.control_id == "4.1").all()
    print(f"Count of '4.1': {len(controls)}")
    
    for c in controls:
        print(f"ID: {c.id} | FwID: {c.framework_id} | Title: {c.title}")
        print(f"   -> Actionable: {c.actionable_title}")
        print(f"   -> Desc: {c.description}")
        
    print("\n--- CHECKING FRAMEWORK 13 (ISO) CONTROLS ---")
    # Assuming ISO is 13 based on previous steps
    iso_controls = db.query(Control).filter(Control.framework_id == 13, Control.control_id == "4.1").all()
    for c in iso_controls:
         print(f"[ISO] ID: {c.id} | Title: {c.title}")
         
    db.close()

if __name__ == "__main__":
    check_duplicates()
