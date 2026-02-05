
import sqlite3
import sys

DB_PATH = "sql_app.db"

def fix_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Beginning Schema Migration: Frameworks Table...")
    
    try:
        # 1. Rename existing table
        cursor.execute("ALTER TABLE frameworks RENAME TO frameworks_old")
        
        # 2. Create NEW table with correct constraints
        # Removed global UNIQUE, added composite UNIQUE(code, tenant_id)
        cursor.execute("""
        CREATE TABLE frameworks (
            id INTEGER NOT NULL PRIMARY KEY, 
            name VARCHAR NOT NULL, 
            code VARCHAR NOT NULL, 
            description TEXT, 
            version VARCHAR, 
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
            updated_at DATETIME, 
            tenant_id VARCHAR DEFAULT 'default_tenant', 
            is_active BOOLEAN DEFAULT 1,
            UNIQUE(code, tenant_id)
        )
        """)
        
        # 3. Copy Data
        print("Migrating Data...")
        cursor.execute("INSERT INTO frameworks SELECT * FROM frameworks_old")
        
        # 4. Drop old table
        cursor.execute("DROP TABLE frameworks_old")
        
        conn.commit()
        print("SUCCESS: Frameworks table migrated with per-tenant uniqueness.")
        
    except Exception as e:
        print(f"MIGRATION FAILED: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_schema()
