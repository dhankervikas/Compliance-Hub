"""
Fix duplicate SOC 2 frameworks.
Problem: seed_soc2.py created 'SOC2' and seed_soc2_full.py created 'SOC2_2017'.
Solution: Move all controls from SOC2_2017 to SOC2, then delete SOC2_2017.
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import Framework, Control

def fix_duplicates():
    db = SessionLocal()
    try:
        print("Fixing duplicate SOC 2 frameworks...")
        
        # 1. Find the frameworks
        original_fw = db.query(Framework).filter(Framework.code == "SOC2").first()
        new_fw = db.query(Framework).filter(Framework.code == "SOC2_2017").first()
        
        if not original_fw:
            print("Original SOC2 framework not found. Nothing to merge into.")
            return

        if not new_fw:
            print("Duplicate SOC2_2017 framework not found. Nothing to fix.")
            # Even if duplicate not found, check if we need to rename original
            if original_fw and original_fw.code == "SOC2" and original_fw.name == "SOC 2 (2017)":
                 print("Renaming Original SOC 2 to full title...")
                 original_fw.name = "SOC 2 - Trust Services Criteria (2017)"
                 original_fw.description = "AICPA Trust Services Criteria for Security, Availability, Processing Integrity, Confidentiality, and Privacy"
                 db.commit()
            return

        print(f"Found Original: {original_fw.name} (ID: {original_fw.id})")
        print(f"Found Duplicate: {new_fw.name} (ID: {new_fw.id})")
        
        # 2. Move controls
        controls_moved = 0
        controls_skipped = 0
        
        for control in new_fw.controls:
            # Check if this control already exists in Original
            existing = db.query(Control).filter(
                Control.framework_id == original_fw.id,
                Control.control_id == control.control_id
            ).first()
            
            if existing:
                print(f"Skipping duplicate control: {control.control_id}")
                controls_skipped += 1
                continue
            
            # Reassign framework ID
            control.framework_id = original_fw.id
            controls_moved += 1
            print(f"Moved control: {control.control_id}")
            
        print(f"Moved {controls_moved} controls. Skipped {controls_skipped} duplicates.")
        
        # 3. Delete the duplicate framework BEFORE renaming the original
        # to avoid Unique Constraint violation
        db.delete(new_fw)
        db.commit()
        print("Successfully deleted duplicate framework.")

        # 4. NOW Rename Original Framework
        print("Renaming Original SOC 2 to full title...")
        original_fw.name = "SOC 2 - Trust Services Criteria (2017)"
        original_fw.description = "AICPA Trust Services Criteria for Security, Availability, Processing Integrity, Confidentiality, and Privacy"
        db.commit()
    
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()
        


if __name__ == "__main__":
    fix_duplicates()
