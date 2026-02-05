
from app.database import SessionLocal
from app.models.control import Control
import sys
import os

sys.path.append(os.getcwd())

def delete_bad_control():
    db = SessionLocal()
    try:
        bad_control = db.query(Control).filter(Control.control_id == 'A.8.35').first()
        if bad_control:
            print(f"Found bad control: {bad_control.control_id} - {bad_control.title}")
            db.delete(bad_control)
            db.commit()
            print("Successfully deleted A.8.35")
        else:
            print("Control A.8.35 not found in DB.")
            
        # Verify count
        count = db.query(Control).filter(Control.control_id.like('A.%')).count()
        print(f"New total count of A. controls: {count}")
        
    finally:
        db.close()

if __name__ == "__main__":
    delete_bad_control()
