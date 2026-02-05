
import sys
import os
import sqlite3

DB_PATH = "sql_app.db"

def check_frameworks():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("--- CHECKING FRAMEWORKS ---")
    cursor.execute("SELECT id, name, code, is_active FROM frameworks")
    fws = cursor.fetchall()
    
    if not fws:
        print("NO FRAMEWORKS FOUND IN DB.")
    else:
        for fw in fws:
            print(f"ID: {fw[0]}, Name: {fw[1]}, Code: {fw[2]}, Is_Active: {fw[3]}")
            
    print("\n--- CHECKING TENANT ENTITLEMENTS (If any) ---")
    # Assuming entitlements might be in a settings table or separate
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tenant_entitlements'")
    if cursor.fetchone():
        cursor.execute("SELECT * FROM tenant_entitlements")
        print(cursor.fetchall())
    else:
        print("No 'tenant_entitlements' table found (Logic might be in frameworks table)")

    conn.close()

if __name__ == "__main__":
    check_frameworks()
