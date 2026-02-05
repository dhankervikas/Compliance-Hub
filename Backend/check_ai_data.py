from app.database import SessionLocal
from app.models.control import Control
from app.models.framework import Framework
from sqlalchemy import func

def verify():
    db = SessionLocal()
    try:
        # Get AI Framework
        fw = db.query(Framework).filter(Framework.code == "AI_FRAMEWORK").first()
        if not fw:
            print("AI Framework not found!")
            return

        print(f"Framework: {fw.name} (ID: {fw.id})")
        
        # Count by Category
        counts = db.query(Control.category, func.count(Control.id))\
            .filter(Control.framework_id == fw.id)\
            .group_by(Control.category)\
            .all()
            
        print("\nControl Counts by Module:")
        print("-" * 30)
        total = 0
        for cat, count in counts:
            print(f"{cat}: {count}")
            total += count
        print("-" * 30)
        print(f"Total: {total}")
        
    finally:
        db.close()

if __name__ == "__main__":
    verify()
