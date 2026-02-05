
import sqlite3
import os

# Database Path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "sql_app.db")

# Config
TARGET_INTERNAL_ID = "a61624c9-b0d9-4125-9bd5-edf7af8fb78e" # testtest tenant
MISSING_FW_IDS = [3, 4, 5, 6] # HIPAA, GDPR, NIST, ISO42001

def repair_entitlements():
    print(f"Connecting to DB: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 1. Verify Tenant Exists
        cursor.execute("SELECT id, name FROM tenants WHERE internal_tenant_id = ?", (TARGET_INTERNAL_ID,))
        tenant = cursor.fetchone()
        if not tenant:
            print("ERROR: Target tenant not found!")
            return
            
        print(f"Repairing entitlements for Tenant: {tenant[1]}")
        
        # 2. Insert Missing Links
        for fw_id in MISSING_FW_IDS:
            # Check if exists (even inactive)
            cursor.execute("""
                SELECT id FROM tenant_frameworks 
                WHERE tenant_id = ? AND framework_id = ?
            """, (TARGET_INTERNAL_ID, fw_id))
            existing = cursor.fetchone()
            
            if existing:
                print(f"Framework {fw_id}: Link exists. Activating...")
                cursor.execute("""
                    UPDATE tenant_frameworks 
                    SET is_active = 1 
                    WHERE tenant_id = ? AND framework_id = ?
                """, (TARGET_INTERNAL_ID, fw_id))
            else:
                print(f"Framework {fw_id}: Creating new link...")
                cursor.execute("""
                    INSERT INTO tenant_frameworks (tenant_id, framework_id, is_active)
                    VALUES (?, ?, 1)
                """, (TARGET_INTERNAL_ID, fw_id))
                
        conn.commit()
        print("SUCCESS: Tenant entitlements repaired!")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    repair_entitlements()
