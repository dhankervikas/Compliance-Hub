from sqlalchemy import text
from app.database import engine

def update_schema():
    print("Updating database schema...")
    with engine.connect() as conn:
        # We need to be outside of a transaction for some ALTER commands or just use autocommit
        conn = conn.execution_options(isolation_level="AUTOCOMMIT")
        
        # Evidence Table Updates
        try:
            conn.execute(text("ALTER TABLE evidence ADD COLUMN status VARCHAR DEFAULT 'pending'"))
            print("[SUCCESS] Added 'status' to evidence")
        except Exception as e:
            print(f"[INFO] 'status' column might already exist: {e}")

        try:
            conn.execute(text("ALTER TABLE evidence ADD COLUMN validation_source VARCHAR DEFAULT 'manual'"))
            print("[SUCCESS] Added 'validation_source' to evidence")
        except Exception as e:
            print(f"[INFO] 'validation_source' column might already exist: {e}")

        # Controls Table Updates
        try:
            conn.execute(text("ALTER TABLE controls ADD COLUMN domain VARCHAR"))
            print("[SUCCESS] Added 'domain' to controls")
        except Exception as e:
            print(f"[INFO] 'domain' column might already exist: {e}")
            
        try:
            conn.execute(text("ALTER TABLE controls ADD COLUMN last_automated_check TIMESTAMP WITH TIME ZONE"))
            print("[SUCCESS] Added 'last_automated_check' to controls")
        except Exception as e:
            print(f"[INFO] 'last_automated_check' column might already exist: {e}")

        try:
            # We use VARCHAR to avoid Enum complexity for existing table
            conn.execute(text("ALTER TABLE controls ADD COLUMN automation_status VARCHAR DEFAULT 'manual'"))
            print("[SUCCESS] Added 'automation_status' to controls")
        except Exception as e:
            print(f"[INFO] 'automation_status' column might already exist: {e}")
            
if __name__ == "__main__":
    update_schema()
