from app.database import SessionLocal
from app.models.framework import Framework
from app.models.control import Control

def analyze_frameworks():
    db = SessionLocal()
    try:
        frameworks = db.query(Framework).all()
        print(f"{'ID':<5} | {'Code':<25} | {'Control Count':<15} | {'Name'}")
        print("-" * 80)
        
        for fw in frameworks:
            count = db.query(Control).filter(Control.framework_id == fw.id).count()
            print(f"{fw.id:<5} | {fw.code:<25} | {count:<15} | {fw.name}")
            
    finally:
        db.close()

if __name__ == "__main__":
    analyze_frameworks()
