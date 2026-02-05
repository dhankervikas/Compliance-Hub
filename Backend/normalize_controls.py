
from app.database import SessionLocal
from app.models.control import Control
import sys
import os

sys.path.append(os.getcwd())

def normalize_controls():
    db = SessionLocal()
    try:
        # Get all ISO- prefixed controls
        iso_controls = db.query(Control).filter(Control.control_id.like('ISO-%')).all()
        print(f"Found {len(iso_controls)} controls with ISO- prefix.")
        
        updated = 0
        deleted = 0
        
        for iso_ctrl in iso_controls:
            target_id = iso_ctrl.control_id.replace("ISO-", "")
            
            # Check if target exists
            existing = db.query(Control).filter(Control.control_id == target_id).first()
            
            if existing:
                # Duplicate! Delete the ISO- one
                print(f"Duplicate found: {target_id} exists. Deleting {iso_ctrl.control_id}...")
                db.delete(iso_ctrl)
                deleted += 1
            else:
                # Rename ISO- one to target
                print(f"Renaming {iso_ctrl.control_id} -> {target_id}")
                iso_ctrl.control_id = target_id
                updated += 1
                
        db.commit()
        print(f"\nCleanup Complete: {updated} renamed, {deleted} deleted.")
        
        # Final Count
        total = db.query(Control).count()
        print(f"Total Controls remaining: {total}")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    normalize_controls()
