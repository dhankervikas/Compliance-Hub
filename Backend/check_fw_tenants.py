
import sqlite3

DB_PATH = "sql_app.db"

def check_fw_tenants():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    print(f"{'ID':<5} | {'Code':<15} | {'Tenant ID':<30} | {'Is Active'}")
    print("-" * 70)
    cursor.execute("SELECT id, code, tenant_id, is_active FROM frameworks")
    for r in cursor.fetchall():
        print(f"{r[0]:<5} | {r[1]:<15} | {r[2]:<30} | {r[3]}")
    conn.close()

if __name__ == "__main__":
    check_fw_tenants()
