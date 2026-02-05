
import sqlite3

DB_PATH = "sql_app.db"

def check_ids():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get Tenant ID for testtest
    cursor.execute("SELECT id, internal_tenant_id FROM tenants WHERE slug = 'testtest'")
    tenant = cursor.fetchone()
    if not tenant:
        print("Tenant testtest not found")
        return

    tenant_uuid = tenant[1]
    print(f"Tenant UUID: {tenant_uuid}")

    cursor.execute("SELECT id, name, code, tenant_id FROM frameworks WHERE tenant_id = ?", (tenant_uuid,))
    rows = cursor.fetchall()
    
    print(f"Found {len(rows)} frameworks for testtest:")
    for r in rows:
        print(f"ID: {r[0]} | Code: {r[2]} | Name: {r[1]}")

if __name__ == "__main__":
    check_ids()
