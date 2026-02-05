
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

db_url = "sqlite:///./sql_app.db"
engine = create_engine(db_url)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

print(f"\n--- Checking Controls for Framework ID 2 (SOC2) ---")
try:
    # Check framework exists
    fw = session.execute(text("SELECT id, name, code FROM frameworks WHERE id = 2")).fetchone()
    if not fw:
        print("Framework ID 2 NOT FOUND.")
    else:
        print(f"Framework: {fw.name} ({fw.code})")

    # Check controls count and is_applicable status
    total = session.execute(text("SELECT count(*) FROM controls WHERE framework_id = 2")).scalar()
    print(f"Total Controls: {total}")
    
    applicable_true = session.execute(text("SELECT count(*) FROM controls WHERE framework_id = 2 AND is_applicable = 1")).scalar()
    print(f"Applicable (True/1): {applicable_true}")
    
    applicable_false = session.execute(text("SELECT count(*) FROM controls WHERE framework_id = 2 AND is_applicable = 0")).scalar()
    print(f"Applicable (False/0): {applicable_false}")
    
    applicable_null = session.execute(text("SELECT count(*) FROM controls WHERE framework_id = 2 AND is_applicable IS NULL")).scalar()
    print(f"Applicable (NULL): {applicable_null}")

    # Dump a few controls to see structure
    controls = session.execute(text("SELECT id, control_id, title, is_applicable FROM controls WHERE framework_id = 2 LIMIT 5")).fetchall()
    print("\nSample Controls:")
    for c in controls:
        print(f"  {c.control_id}: Applicable={c.is_applicable}")

except Exception as e:
    print(f"Error: {e}")
finally:
    session.close()
