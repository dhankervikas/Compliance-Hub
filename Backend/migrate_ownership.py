import sqlite3
import os

DB_PATH = "C:/Users/dhank/OneDrive/Documents/Compliance_Product/Backend/sql_app.db"

def migrate_db():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # List tables
    print("Existing tables:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(tables)
    
    print("Checking for missing columns in 'controls' table...")
    
    if ('controls',) not in tables:
        print("ERROR: 'controls' table not found in DB.")
        return

    # Get existing columns
    cursor.execute("PRAGMA table_info(controls)")
    columns = [info[1] for info in cursor.fetchall()]
    
    # Add owner_id if missing
    if "owner_id" not in columns:
        print("Adding 'owner_id' column...")
        cursor.execute("ALTER TABLE controls ADD COLUMN owner_id VARCHAR")
    else:
        print("'owner_id' column already exists.")

    # Add department_id if missing
    if "department_id" not in columns:
        print("Adding 'department_id' column...")
        cursor.execute("ALTER TABLE controls ADD COLUMN department_id VARCHAR")
    else:
        print("'department_id' column already exists.")
        
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate_db()
