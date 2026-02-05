
import sys
import os
import sqlite3

# Database Path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "sql_app.db")

print(f"Connecting to SQLite DB: {DB_PATH}")

def check_frameworks():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        print("\n--- TENANTS ---")
        cursor.execute("SELECT id, name, slug, internal_tenant_id FROM tenants")
        tenants = cursor.fetchall()
        for t in tenants:
            print(f"ID: {t[0]} | Name: {t[1]} | Slug: {t[2]} | Internal ID: {t[3]}")
            
        print("\n--- FRAMEWORKS ---")
        cursor.execute("SELECT id, name, code FROM frameworks")
        frameworks = cursor.fetchall()
        for fw in frameworks:
            print(f"ID: {fw[0]} | Name: {fw[1]} | Code: {fw[2]}")
            
        print("\n--- TENANT FRAMEWORKS (Links) ---")
        cursor.execute("SELECT tenant_id, framework_id, is_active FROM tenant_frameworks")
        links = cursor.fetchall()
        for l in links:
            print(f"Tenant Internal ID: {l[0]} | Framework ID: {l[1]} | Active: {l[2]}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_frameworks()
