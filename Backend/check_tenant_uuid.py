
import sqlite3

DB_PATH = "sql_app.db"

def check_tenant():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check tenants table structure first? No, assume standard 'tenants' table
        cursor.execute("SELECT * FROM tenants WHERE name = 'testtest' OR slug = 'testtest'")
        tenant = cursor.fetchone()
        
        if tenant:
            print(f"FOUND TENANT: {tenant}")
        else:
            print("TENANT 'testtest' NOT FOUND in DB.")
            
            # List all tenants
            print("Listing ALL tenants:")
            cursor.execute("SELECT id, name, slug FROM tenants") # guessing columns
            rows = cursor.fetchall()
            for r in rows:
                print(r)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    check_tenant()
