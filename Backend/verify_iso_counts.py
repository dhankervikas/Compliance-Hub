
from app.database import SessionLocal
from app.models.control import Control
from app.models.framework import Framework
from sqlalchemy import func

def verify_iso():
    db = SessionLocal()
    try:
        fw = db.query(Framework).filter(Framework.code == "ISO27001").first()
        if not fw:
            # Try searching by name if code differs
            fw = db.query(Framework).filter(Framework.name.like("%ISO%27001%")).first()
            
        if not fw:
            print("ISO 27001 Framework not found!")
            return

        print(f"Framework: {fw.name} (Code: {fw.code}, ID: {fw.id})")
        
        # Total count
        total = db.query(Control).filter(Control.framework_id == fw.id).count()
        print(f"Total Controls in DB: {total}")
        
        # Breakdown by ID Prefix
        controls = db.query(Control).filter(Control.framework_id == fw.id).all()
        
        prefix_counts = {}
        for c in controls:
            # Extract prefix (e.g., "A.5", "4.1")
            parts = c.control_id.split('.')
            if c.control_id.startswith("A"):
                prefix = f"{parts[0]}.{parts[1]}" # A.5
            else:
                prefix = parts[0] # 4, 5, etc.
                
            prefix_counts[prefix] = prefix_counts.get(prefix, 0) + 1
            
        print("\nControl Counts by Prefix:")
        print("-" * 30)
        for prefix in sorted(prefix_counts.keys()):
            print(f"{prefix}: {prefix_counts[prefix]}")
        print("-" * 30)

    finally:
        db.close()

if __name__ == "__main__":
    verify_iso()
