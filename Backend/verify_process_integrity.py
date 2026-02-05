from sqlalchemy import create_engine
from sqlalchemy.orm import joinedload, sessionmaker
from app.database import Base
from app.config import settings
from app.models.control import Control
from app.models.process import Process, SubProcess
from app.models.framework import Framework
from collections import Counter

# Setup DB
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def verify_integrity():
    print("[-] Verifying ISO 27001 Process Integrity...")
    
    # Get ISO Framework
    iso = db.query(Framework).filter(Framework.code.like("ISO27001%")).first()
    if not iso:
        print("ISO Framework not found")
        return

    # Fetch all ISO controls
    controls = db.query(Control).options(
        joinedload(Control.sub_processes).joinedload(SubProcess.process)
    ).filter(
        Control.framework_id == iso.id
    ).all()
    
    total = len(controls)
    uncategorized = []
    category_counts = Counter()

    for c in controls:
        p_name = c.process_name
        if not p_name:
            uncategorized.append(c.control_id)
            category_counts["Uncategorized"] += 1
        else:
            category_counts[p_name] += 1
            
    print(f"\nTotal ISO Controls: {total}")
    print(f"Mapped Successfully: {total - len(uncategorized)}")
    print(f"Uncategorized: {len(uncategorized)}")
    
    if uncategorized:
        print("\n[!] Uncategorized Controls (Need Mapping):")
        print(uncategorized[:20]) # Show first 20
        if len(uncategorized) > 20:
            print(f"... and {len(uncategorized) - 20} more.")
            
    print("\n[+] Grouping Distribution:")
    for cat, count in category_counts.most_common():
        print(f"  - {cat}: {count}")

if __name__ == "__main__":
    verify_integrity()
