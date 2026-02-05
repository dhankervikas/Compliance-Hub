
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import json

db_url = "sqlite:///./sql_app.db"
engine = create_engine(db_url)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

print(f"\n--- Checking Settings ---")
try:
    # Check settings table
    result = session.execute(text("SELECT key, value FROM settings WHERE key = 'scope'")).fetchone()
    if result:
        print(f"Found Scope Settings:")
        # Value is likely JSON string
        try:
            data = json.loads(result.value)
            print(json.dumps(data, indent=2))
        except:
            print(f"Raw Value: {result.value}")
    else:
        print("No 'scope' settings found in DB.")

except Exception as e:
    print(f"Error: {e}")
finally:
    session.close()
