
import sqlite3

DB_PATH = "sql_app.db"

def check_control_tenants():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    print(f"{'Count':<10} | {'Tenant ID'}")
    print("-" * 40)
    cursor.execute("SELECT count(*), tenant_id FROM controls GROUP BY tenant_id")
    for r in cursor.fetchall():
        print(f"{r[0]:<10} | {r[1]}")
    conn.close()

if __name__ == "__main__":
    check_control_tenants()
