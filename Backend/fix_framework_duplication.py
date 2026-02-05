
from app.database import SessionLocal
from app.models.framework import Framework
from app.models.control import Control

db = SessionLocal()
try:
    # Target: ID 12 (Duplicate)
    duplicate_fw = db.query(Framework).filter(Framework.id == 12).first()
    
    if duplicate_fw:
        print(f"Deleting Duplicate Framework: {duplicate_fw.name} (ID: {duplicate_fw.id})")
        
        # Delete associated controls first (Cascade usually handles this, but explicit is safer)
        controls = db.query(Control).filter(Control.framework_id == 12).all()
        print(f"Deleting {len(controls)} controls associated with this framework.")
        for c in controls:
            db.delete(c)
            
        # Delete Framework
        db.delete(duplicate_fw)
        db.commit()
        print("Successfully deleted duplicate framework.")
    else:
        print("Duplicate Framework ID 12 not found.")

finally:
    db.close()
