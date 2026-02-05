
import sqlite3

DB_PATH = "sql_app.db"

def check_links():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    print(f"{'Tenant ID':<38} | {'FW ID':<5} | {'Active'}")
    print("-" * 60)
    try:
        cursor.execute("SELECT tenant_id, framework_id, is_active FROM tenant_frameworks")
        for r in cursor.fetchall():
            print(f"{r[0]:<38} | {r[1]:<5} | {r[2]}")
    except sqlite3.OperationalError:
        print("Table 'tenant_frameworks' not found or error accessing it.")
        
    conn.close()

if __name__ == "__main__":
    check_links()
