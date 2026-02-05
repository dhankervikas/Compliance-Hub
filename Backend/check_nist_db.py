from app.database import SessionLocal
from app.models import Control, Framework

def check():
    db = SessionLocal()
    fw = db.query(Framework).filter(Framework.name == "NIST CSF 2.0").first()
    if not fw:
        print("Framework not found")
        return

    controls = db.query(Control).filter(Control.framework_id == fw.id).all()
    print(f"Total Controls: {len(controls)}")
    
    functions = [c.control_id for c in controls if len(c.control_id) == 2]
    categories = [c.control_id for c in controls if len(c.control_id) == 5]
    subcats = [c.control_id for c in controls if len(c.control_id) > 5]
    
    print(f"Functions ({len(functions)}): {functions}")
    print(f"Categories ({len(categories)}): {categories}")
    print(f"Subcategories ({len(subcats)} total)")

if __name__ == "__main__":
    check()
