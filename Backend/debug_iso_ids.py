from app.database import SessionLocal
from app.models.control import Control

def debug_ids():
    db = SessionLocal()
    print("--- DEBUG ISO CONTROL IDS ---")
    controls = db.query(Control).filter(Control.framework_id == 1).all()
    print(f"Total ISO Controls: {len(controls)}")
    
    if controls:
        print("First 10 IDs:")
        for c in controls[:10]:
            print(f"ID: '{c.control_id}' | Title: {c.title}")
            
    # Check for A.5.1 specifically
    target = db.query(Control).filter(Control.control_id == "A.5.1").first()
    if target:
        print(f"\nFound A.5.1 directly. Framework ID: {target.framework_id}")
    else:
        print("\nCould NOT find 'A.5.1' by exact string match.")
        
    db.close()

if __name__ == "__main__":
    debug_ids()
