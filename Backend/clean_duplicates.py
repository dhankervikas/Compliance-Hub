from app.database import SessionLocal
from app.models.framework import Framework
from app.models.control import Control

def clean_duplicates():
    db = SessionLocal()
    try:
        print("--- Duplicate Cleanup ---")
        
        # Find all ISO frameworks
        isos = db.query(Framework).filter(Framework.name.like("%ISO%27001%")).all()
        
        print(f"Found {len(isos)} ISO frameworks.")
        
        for fw in isos:
            count = db.query(Control).filter(Control.framework_id == fw.id).count()
            print(f"ID {fw.id}: '{fw.name}' (Code: {fw.code}) - {count} controls")
            
            if count == 0:
                print(f" -> Deleting empty framework ID {fw.id}...")
                db.delete(fw)
                db.commit()
                print("    [DELETED]")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()
        print("--- Cleanup Done ---")

if __name__ == "__main__":
    clean_duplicates()
