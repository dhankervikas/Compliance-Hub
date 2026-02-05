from app.database import SessionLocal
from app.models.control import Control
from app.models.framework import Framework
from sqlalchemy import or_

def reset_iso():
    db = SessionLocal()
    try:
        fws = db.query(Framework).filter(
            or_(Framework.code == "ISO27001", Framework.code == "ISO27001_ISMS")
        ).all()
        
        for fw in fws:
            print(f"Resetting controls for Framework: {fw.name} ({fw.code})")
            deleted = db.query(Control).filter(Control.framework_id == fw.id).delete()
            print(f"Deleted {deleted} controls.")
            
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    reset_iso()
