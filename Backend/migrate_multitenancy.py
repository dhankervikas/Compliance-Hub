import sqlite3
import os

# Database Path
DB_PATH = "sql_app.db"

# Tables to migrate
TABLES = [
    "frameworks",
    "controls",
    "policies",
    "evidence",
    "assessments",
    "documents"
]

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] Database file not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print(f"--- MIGRATING DATABASE FOR MULTITENANCY ---")
    
    for table in TABLES:
        try:
            print(f"Checking table: {table}...")
            
            # Check if column exists
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [info[1] for info in cursor.fetchall()]
            
            if "tenant_id" in columns:
                print(f"  [SKIP] 'tenant_id' already exists in {table}.")
            else:
                print(f"  [MIGRATE] Adding 'tenant_id' to {table}...")
                # SQLite ALTER TABLE to add column
                # We set DEFAULT 'default_tenant' for existing records
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN tenant_id VARCHAR DEFAULT 'default_tenant'")
                
                # Check for NOT NULL constraint if strictly required, but for SQLite add column usually handles default
                # We can also explicitly update NULLs just in case
                cursor.execute(f"UPDATE {table} SET tenant_id = 'default_tenant' WHERE tenant_id IS NULL")
                
                print(f"  [SUCCESS] Updated {table}.")
                
        except Exception as e:
            print(f"  [ERROR] Failed to update {table}: {e}")

    conn.commit()
    conn.close()
    print("--- MIGRATION COMPLETE ---")

if __name__ == "__main__":
    migrate()
