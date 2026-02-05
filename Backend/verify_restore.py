from sqlalchemy import create_engine, text
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
with engine.connect() as conn:
    print("--- VERIFICATION ---")
    
    # 1. Count Processes
    res = conn.execute(text("SELECT count(*) FROM processes WHERE framework_code='ISO27001'"))
    count = res.scalar()
    print(f"ISO Processes: {count} (Expected: 21)")
    
    # 2. Check Specific Process Names
    res = conn.execute(text("SELECT name FROM processes WHERE framework_code='ISO27001' ORDER BY name"))
    names = [r[0] for r in res]
    print(f"Process List Sample: {names[:5]}")
    if "Internal Audit" in names and "Management Review" in names:
        print("[OK] 'Internal Audit' and 'Management Review' are present.")
    else:
        print(f"[FAIL] Essential Processes MISSING. Found: {names}")
        
    # 3. Check Action Titles
    res = conn.execute(text("SELECT title, description FROM controls WHERE control_id='A.8.10'"))
    row = res.first()
    if row:
        print(f"A.8.10 Title: '{row[0]}'")
        if "Dispose" in row[0]:
            print("[OK] Action Title Applied.")
        else:
            print("[FAIL] Action Title Mismatch.")
    else:
        print("[WARN] A.8.10 not found (might be missing in CSV).")

    # 4. Count Controls
    # res = conn.execute(text("SELECT count(*) FROM controls WHERE framework_id=13")) 
    res = conn.execute(text("SELECT count(*) FROM controls"))
    print(f"Total Controls: {res.scalar()}")
