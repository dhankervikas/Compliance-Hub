from app.database import SessionLocal
from app.models.control import Control
from app.models.process import process_control_mapping
from sqlalchemy import text

def verify_mapping():
    db = SessionLocal()
    print("--- CHECKING CLAUSE 4 MAPPINGS ---")
    
    # Check 4.1, 4.2, 4.3, 4.4
    clauses = ["4.1", "4.2", "4.3", "4.4"]
    
    for cid in clauses:
        c = db.query(Control).filter(Control.control_id == cid).first()
        if not c:
            print(f"{cid} NOT FOUND in DB.")
            continue
            
        # Check mapping
        # We can query the M2M table
        sql = text("SELECT process_id FROM process_control_mapping WHERE control_id = :cid")
        result = db.execute(sql, {"cid": c.id}).fetchall()
        
        mapped = "YES" if result else "NO"
        print(f"Control {cid}: Mapped? {mapped} | Title: {c.title}")

    db.close()

if __name__ == "__main__":
    verify_mapping()
