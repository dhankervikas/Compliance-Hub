
from app.database import SessionLocal
from app.models.control import Control
from sqlalchemy import or_

def cleanup():
    db = SessionLocal()
    try:
        # Find old controls
        to_delete = db.query(Control).filter(
            Control.control_id.in_(["9.2", "9.3"]),
            Control.category == "Clause 9: Performance evaluation" 
        ).all()
        
        count = len(to_delete)
        if count > 0:
            print(f"Deleting {count} old controls: {[c.control_id for c in to_delete]}")
            for c in to_delete:
                db.delete(c)
            db.commit()
            print("Deletion complete.")
        else:
            print("No old controls found to delete.")
            
    finally:
        db.close()

if __name__ == "__main__":
    cleanup()
