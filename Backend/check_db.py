
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Try sql_app.db first, then compliance.db
dbs = ["sqlite:///./sql_app.db", "sqlite:///./compliance.db"]

for db_url in dbs:
    print(f"\n--- Checking {db_url} ---")
    try:
        engine = create_engine(db_url)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        # Check Frameworks
        result = session.execute(text("SELECT id, name, code FROM frameworks"))
        frameworks = result.fetchall()
        print(f"Frameworks ({len(frameworks)}):")
        for f in frameworks:
            print(f"  ID: {f.id}, Name: {f.name}, Code: {f.code}")
            
            # Count controls for this framework
            count = session.execute(text(f"SELECT count(*) FROM controls WHERE framework_id = {f.id}")).scalar()
            print(f"    Controls Count: {count}")

        # Check for stranded controls (no framework or invalid framework)
        orphaned = session.execute(text("SELECT count(*) FROM controls WHERE framework_id IS NULL")).scalar()
        print(f"Orphaned Controls (NULL framework_id): {orphaned}")
        
        session.close()
    except Exception as e:
        print(f"Error checking {db_url}: {e}")
