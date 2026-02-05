from app.database import SessionLocal
from app.models.control import Control

def check_ids():
    db = SessionLocal()
    fw1 = db.query(Control).filter(Control.framework_id == 1).limit(5).all()
    fw3 = db.query(Control).filter(Control.framework_id == 3).limit(5).all()
    
    print("FW 1 (Annex A):")
    for c in fw1:
        print(f" - {c.control_id}: {c.title}")

    print("\nFW 3 (ISMS):")
    for c in fw3:
        print(f" - {c.control_id}: {c.title}")

if __name__ == "__main__":
    check_ids()
