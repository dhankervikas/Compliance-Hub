import sqlite3

DB_PATH = "sql_app.db"
TARGET_TENANT = "a61624c9-b0d9-4125-9bd5-edf7af8fb78e"

def fix():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get frameworks for this tenant
    cursor.execute("SELECT id, code FROM frameworks WHERE tenant_id = ?", (TARGET_TENANT,))
    frameworks = cursor.fetchall()
    
    print(f"Found {len(frameworks)} frameworks for tenant {TARGET_TENANT}")
    
    count = 0
    for fw_id, code in frameworks:
        # Check if link exists
        cursor.execute("SELECT id FROM tenant_frameworks WHERE tenant_id = ? AND framework_id = ?", (TARGET_TENANT, fw_id))
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Linking {code} (ID: {fw_id})...")
            cursor.execute("""
                INSERT INTO tenant_frameworks (tenant_id, framework_id, is_active, is_locked, created_at, updated_at)
                VALUES (?, ?, 1, 0, datetime('now'), datetime('now'))
            """, (TARGET_TENANT, fw_id))
            count += 1
            
    conn.commit()
    conn.close()
    print(f"Fixed {count} missing links.")

if __name__ == "__main__":
    fix()
