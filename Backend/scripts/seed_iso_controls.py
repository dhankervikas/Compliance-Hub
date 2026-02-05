import sys
import os
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine
from app.models.control import Control
from app.utils.iso_data import ISO_CONTROLS_DATA

def seed_controls():
    db = SessionLocal()
    try:
        print("Seeding ISO 27001 Annex A Controls...")
        
        # Get Framework ID
        from app.models.framework import Framework
        iso_framework = db.query(Framework).filter(Framework.name.like("%ISO%27001%")).first()
        if not iso_framework:
            print("Error: ISO 27001 framework not found. Please create it first.")
            return
        
        framework_id = iso_framework.id
        print(f"Using Framework ID: {framework_id}")

        count = 0
        updated = 0
        
        for data in ISO_CONTROLS_DATA:
            # We ONLY want Annex A controls for SoA (starting with "A.")
            if not data["control_id"].startswith("A."):
                continue

            control = db.query(Control).filter(Control.control_id == data["control_id"]).first()
            if not control:
                print(f"Creating {data['control_id']}...")
                control = Control(
                    control_id=data["control_id"],
                    title=data["title"],
                    description=data["description"],
                    category=data["category"],
                    priority=data["priority"],
                    classification=data["classification"],
                    framework_id=framework_id,  # ADDED
                    # Default SoA fields
                    is_applicable=True,
                    justification_reason="",
                    justification="",
                    implementation_method=""
                )
                db.add(control)
                count += 1
            else:
                # Optional: Update metadata if changed, but preserve user SoA choices
                # For now, we just ensure they exist.
                pass
        
        db.commit()
        print(f"Seeding complete. Added {count} new controls.")
        
        # Verify total count
        total = db.query(Control).filter(Control.control_id.like("A.%")).count()
        print(f"Total Annex A Controls in DB: {total}")
        
    except Exception as e:
        print(f"Error seeding controls: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_controls()
