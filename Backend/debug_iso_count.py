from app.database import SessionLocal
from app.models.control import Control
from app.models.framework import Framework

def check():
    db = SessionLocal()
    try:
        fw = db.query(Framework).filter(Framework.code == "ISO27001").first()
        if not fw:
            print("Framework not found")
            return
            
        ctrls = db.query(Control).filter(Control.framework_id == fw.id).all()
        print(f"Total Controls: {len(ctrls)}")
        
        clauses = [c.control_id for c in ctrls if c.control_id[0].isdigit()]
        annex = [c.control_id for c in ctrls if c.control_id.startswith("A.")]
        
        print(f"Annex A Count: {len(annex)}")
        print(f"Clause Count: {len(clauses)}")
        print(f"Clauses present: {sorted(clauses)}")
        
    finally:
        db.close()

if __name__ == "__main__":
    check()
