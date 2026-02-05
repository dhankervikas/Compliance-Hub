
import sqlite3
import sys

DB_PATH = "sql_app.db"

def fix_control_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Beginning Schema Migration: Controls Table...")
    
    try:
        # 1. Rename existing table
        cursor.execute("ALTER TABLE controls RENAME TO controls_old")
        
        # 2. Create NEW table with correct constraints
        # Removed global UNIQUE(control_id), added composite UNIQUE(control_id, tenant_id)
        # Assuming typical columns based on seed script
        cursor.execute("""
        CREATE TABLE controls (
            id INTEGER NOT NULL PRIMARY KEY, 
            control_id VARCHAR NOT NULL, 
            title VARCHAR NOT NULL, 
            description TEXT, 
            ai_explanation TEXT, 
            ai_requirements_json TEXT, 
            framework_id INTEGER NOT NULL, 
            status VARCHAR(11), 
            owner VARCHAR, 
            implementation_notes TEXT, 
            category VARCHAR, 
            priority VARCHAR, 
            is_applicable BOOLEAN, 
            justification TEXT, 
            justification_reason VARCHAR, 
            implementation_method TEXT, 
            domain VARCHAR, 
            classification VARCHAR, 
            automation_status VARCHAR, 
            last_automated_check DATETIME, 
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
            updated_at DATETIME, 
            tenant_id VARCHAR DEFAULT 'default_tenant', 
            owner_id VARCHAR, 
            department_id VARCHAR,
            UNIQUE(control_id, tenant_id),
            FOREIGN KEY(framework_id) REFERENCES frameworks(id)
        )
        """)
        
        # 3. Copy Data
        print("Migrating Data...")
        cursor.execute("INSERT INTO controls SELECT * FROM controls_old")
        
        # 4. Drop old table
        cursor.execute("DROP TABLE controls_old")
        
        conn.commit()
        print("SUCCESS: Controls table migrated with per-tenant uniqueness.")
        
    except Exception as e:
        print(f"MIGRATION FAILED: {e}")
        conn.rollback()
        # Restore old table
        try:
            cursor.execute("DROP TABLE controls") # Drop incomplete new
            cursor.execute("ALTER TABLE controls_old RENAME TO controls")
            conn.commit()
            print("ROLLED BACK: Original controls table restored.")
        except Exception as rb_e:
            print(f"CRITICAL ROLLBACK FAILURE: {rb_e}")
            
    finally:
        conn.close()

if __name__ == "__main__":
    fix_control_schema()
