import sys
from sqlalchemy import text
from app.database import SessionLocal, engine
from app.models.framework import Framework
from app.models.control import Control
from app.models.control_mapping import ControlMapping

def fix_data():
    db = SessionLocal()
    try:
        print("Starting SOC 2 Data Cleanup...")
        
        # 1. Find and Delete Duplicate Framework (SOC2_2017)
        dup_fw = db.query(Framework).filter(Framework.code == "SOC2_2017").first()
        if dup_fw:
            print(f"Found duplicate framework ID: {dup_fw.id} ({dup_fw.code})")
            
            # Delete mappings first
            # We use raw SQL for safety/speed if ORM fails
            db.execute(text("DELETE FROM control_mappings WHERE source_control_id IN (SELECT id FROM controls WHERE framework_id = :fw_id) OR target_control_id IN (SELECT id FROM controls WHERE framework_id = :fw_id)"), {"fw_id": dup_fw.id})
            
            # Delete controls
            db.execute(text("DELETE FROM controls WHERE framework_id = :fw_id"), {"fw_id": dup_fw.id})
            
            # Delete framework
            db.delete(dup_fw)
            db.commit()
            print("Deleted duplicate framework.")
            
        # 2. Clear Old Controls from Real Framework (SOC2)
        real_fw = db.query(Framework).filter(Framework.code == "SOC2").first()
        if real_fw:
            print(f"Found real framework ID: {real_fw.id} ({real_fw.code})")
            # Delete existing controls (likely the old COSO ones)
            db.execute(text("DELETE FROM control_mappings WHERE source_control_id IN (SELECT id FROM controls WHERE framework_id = :fw_id) OR target_control_id IN (SELECT id FROM controls WHERE framework_id = :fw_id)"), {"fw_id": real_fw.id})
            db.execute(text("DELETE FROM controls WHERE framework_id = :fw_id"), {"fw_id": real_fw.id})
            db.commit()
            print("Cleared old controls from SOC 2 framework.")
        else:
            print("Real SOC2 framework not found (will be created by seed).")

        print("Cleanup Complete.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_data()
