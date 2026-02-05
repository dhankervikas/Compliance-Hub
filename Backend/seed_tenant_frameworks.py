
import sqlite3
import uuid
import json
from datetime import datetime

DB_PATH = "sql_app.db"
SOURCE_TENANT = "5c388945-3ebb-4856-99d9-ebf2f448ae73" # Default Tenant
TARGET_TENANT = "a61624c9-b0d9-4125-9bd5-edf7af8fb78e" # TestTest

def clone_frameworks():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 1. Get Source Frameworks
    cursor.execute("SELECT * FROM frameworks WHERE tenant_id = ?", (SOURCE_TENANT,))
    frameworks = cursor.fetchall()
    
    print(f"Found {len(frameworks)} frameworks for Default Tenant. Cloning to {TARGET_TENANT}...")
    
    fw_map = {} # OldID -> NewID
    
    for fw in frameworks:
        # Check if already exists in target
        cursor.execute("SELECT id FROM frameworks WHERE code = ? AND tenant_id = ?", (fw['code'], TARGET_TENANT))
        existing = cursor.fetchone()
        if existing:
            print(f"Skipping {fw['code']} (Already exists)")
            fw_map[fw['id']] = existing[0]
            continue
            
        print(f"Cloning Framework: {fw['name']}")
        cursor.execute("""
            INSERT INTO frameworks (name, code, description, version, tenant_id, is_active, created_at, updated_at) 
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """, (fw['name'], fw['code'], fw['description'], fw['version'], TARGET_TENANT, 1)) # Force Active
        new_id = cursor.lastrowid
        fw_map[fw['id']] = new_id

    # 2. Clone Controls
    print("Cloning Controls...")
    cursor.execute("SELECT * FROM controls WHERE tenant_id = ?", (SOURCE_TENANT,)) # Or implicit
    # Actually, controls usually have tenant_id matching framework.
    # Let's get controls by framework_id from source
    
    for old_fw_id, new_fw_id in fw_map.items():
        if old_fw_id == new_fw_id: continue # Skipped copy
        
        cursor.execute("SELECT * FROM controls WHERE framework_id = ?", (old_fw_id,))
        controls = cursor.fetchall()
        print(f"  -> Cloning {len(controls)} controls for FW {new_fw_id}...")
        
        for c in controls:
            cursor.execute("""
                INSERT INTO controls (
                    control_id, title, description, tenant_id, framework_id, status, 
                    owner, category, priority, is_applicable, justification, 
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            """, (
                c['control_id'], c['title'], c['description'], TARGET_TENANT, new_fw_id, 'not_started',
                c['owner'], c['category'], c['priority'], 1, c['justification']
            ))

    conn.commit()
    conn.close()
    print("Cloning Complete.")

if __name__ == "__main__":
    clone_frameworks()
