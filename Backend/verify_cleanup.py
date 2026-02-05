
from app.database import SessionLocal
from app.models.control import Control
import sys
import os

sys.path.append(os.getcwd())

def verify_clean_clauses():
    db = SessionLocal()
    try:
        # Count ISO- prefixed
        iso_count = db.query(Control).filter(Control.control_id.like('ISO-%')).count()
        print(f"ISO- prefixed controls count: {iso_count}")
        
        # Count clean Annex A
        annex_count = db.query(Control).filter(Control.control_id.like('A.%')).filter(Control.control_id.notlike('ISO-%')).count()
        print(f"Clean Annex A count: {annex_count}")
        
        # Count clean Clauses (starts with digit)
        # SQLAlchemy doesn't have regex easy, so list and count
        all_controls = db.query(Control).all()
        clean_clauses = [c for c in all_controls if c.control_id[0].isdigit() and not c.control_id.startswith('ISO')]
        print(f"Clean Clauses 4-10 count: {len(clean_clauses)}")
        
        if len(clean_clauses) > 20:
            print("SAFE TO DELETE ISO-%")
        else:
            print("WARNING: Not enough clean clauses found!")
            for c in clean_clauses:
                print(c.control_id)

    finally:
        db.close()

if __name__ == "__main__":
    verify_clean_clauses()
