from sqlalchemy import create_engine
from sqlalchemy.orm import joinedload, sessionmaker
from app.database import Base
from app.config import settings
from app.models.control import Control
from app.models.process import Process, SubProcess
from app.models.framework import Framework

# Setup DB
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def debug_mappings():
    print("[-] Debugging ISO 27001 Process Mappings...")
    
    # Get ISO Framework
    # Note: framework code might be "ISO27001" or "ISO27001:2022" depending on seed
    iso = db.query(Framework).filter(Framework.code.like("ISO27001%")).first()
    if not iso:
        print("ISO Framework not found")
        return

    print(f"Framework: {iso.name} (ID: {iso.id})")

    # Check Clause 6 (Risk)
    print("\n--- Clause 6 (Risk Management) ---")
    controls = db.query(Control).options(
        joinedload(Control.sub_processes).joinedload(SubProcess.process)
    ).filter(
        Control.framework_id == iso.id,
        Control.control_id.like("6.%")
    ).all()
    
    print(f"Found {len(controls)} controls in Clause 6")
    for c in controls:
        p_name = c.process_name # Property
        print(f"[{c.control_id}] {c.title}")
        print(f"    Domain: {c.domain}")
        print(f"    Process Name (Property): {p_name}")

    # Check Annex A.7 (Physical)
    print("\n--- Annex A.7 (Physical) ---")
    controls = db.query(Control).options(
         joinedload(Control.sub_processes).joinedload(SubProcess.process)
    ).filter(
        Control.framework_id == iso.id,
        Control.control_id.like("A.7%")
    ).all()
    
    for c in controls:
        p_name = c.process_name
        print(f"[{c.control_id}] {c.title}")
        print(f"    Process Name (Property): {p_name}")

if __name__ == "__main__":
    debug_mappings()
