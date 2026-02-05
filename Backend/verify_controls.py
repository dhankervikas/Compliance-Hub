
import sqlite3
import os

# Database Path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Adjust path to DB relative to Backend/ folder if script is running from root or Backend
if os.path.exists(os.path.join(BASE_DIR, "sql_app.db")):
    DB_PATH = os.path.join(BASE_DIR, "sql_app.db")
else:
    # Fallback usually for running from root
    DB_PATH = os.path.join(BASE_DIR, "Backend", "sql_app.db")
    if not os.path.exists(DB_PATH):
         # Try one level up if inside backend
         DB_PATH = os.path.join(os.path.dirname(BASE_DIR), "sql_app.db")

# Framework IDs from previous steps:
# 5: NIST CSF at ID 5 (from verify logs)
# 6: ISO 42001 at ID 6
FRAMEWORK_IDS = [5, 6] 
TENANT_SLUG = "testtest"

def verify_controls():
    print(f"Connecting to DB: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("DB File not found at path!")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Get internal ID for tenant
        cursor.execute("SELECT internal_tenant_id FROM tenants WHERE slug = ?", (TENANT_SLUG,))
        row = cursor.fetchone()
        if not row:
            print("Tenant found not found")
            print("\n--- All Controls Distribution by Tenant ---")
            rows = cursor.execute("SELECT tenant_id, framework_id, COUNT(*) FROM controls GROUP BY tenant_id, framework_id").fetchall()
            for r in rows:
                print(f"Tenant: {r[0]}, Framework: {r[1]}, Count: {r[2]}")
                
            print("\n--- NIST Sample ---")
            rows = cursor.execute("SELECT control_id, tenant_id FROM controls WHERE framework_id='NIST_CSF' OR control_id LIKE 'ID.%' LIMIT 5").fetchall()
            for r in rows:
                print(f"ID: {r[0]}, Tenant: {r[1]}")
            return
        internal_id = row[0]
        print(f"Tenant Internal ID: {internal_id}")
        
        for fw_id in FRAMEWORK_IDS:
             cursor.execute("SELECT name, code FROM frameworks WHERE id = ?", (fw_id,))
             fw = cursor.fetchone()
             fw_name = fw[0] if fw else "Unknown"
             
             # Count controls for this tenant
             cursor.execute("""
                SELECT count(*) FROM controls 
                WHERE framework_id = ? AND tenant_id = ?
             """, (fw_id, TENANT_SLUG)) # Note: Control.tenant_id usually uses SLUG based on previous code checks (User.tenant_id is slug)
             # Wait, checking models.py will confirm if it uses slug or internal_id. 
             # App.js seeding usually sends payload with headers. Backend verify_tenant usually sets state.tenant_id to slug?
             # Let's check both possibilities in the query or just print sample
             
             count_slug = cursor.fetchone()[0]
             
             print(f"Framework {fw_id} ({fw_name}): {count_slug} controls found for tenant '{TENANT_SLUG}'")

             # Check for "public" controls (null tenant_id?)
             cursor.execute("SELECT count(*) FROM controls WHERE framework_id = ? AND tenant_id IS NULL", (fw_id,))
             count_null = cursor.fetchone()[0]
             print(f"  (Global/Null Tenant Controls: {count_null})")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    verify_controls()
