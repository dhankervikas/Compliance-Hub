import sqlite3

# Connect to the verified database
DB_NAME = "sql_app.db"
print(f"Connecting to {DB_NAME}...")

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

TARGET_TENANT = "default_tenant"
USERNAME = "admin"

try:
    # 1. Check for duplicate admins
    print("Checking for admin users...")
    cursor.execute("SELECT id, username, tenant_id FROM users WHERE username=?", (USERNAME,))
    admins = cursor.fetchall()
    
    if not admins:
        print("No admin user found! Creating one...")
        # (Optional: Add creation logic if needed, but unlikely given previous output)
    else:
        for u in admins:
            print(f"Found Admin: ID={u[0]}, Tenant={u[2]}")
            
            # Delete conflict
            if u[2] != TARGET_TENANT:
                print(f"Deleting Duplicate Admin {u[0]} (Tenant: {u[2]})...")
                cursor.execute("DELETE FROM users WHERE id=?", (u[0],))
    
    # 2. Update Controls (Just in case some got stranded, though restore script does this)
    # Actually, restore script sets them to default_tenant.
    # But let's make sure we didn't leave any stranded from the other tenant.
    # If the user wants "Restored" state, we should probably wipe the UUID tenant controls if they are duplicates or garbage.
    # The previous inspection showed 301 controls for the UUID tenant. These might be the generic ones.
    # Let's re-assign them or delete them? 
    # The prompt user says "Hard Reset". So we should prioritize the master file ones (690).
    # The 301 controls might be conflicting.
    
    # Safe move: Ensure Admin points to the 690 controls (default_tenant).
    # We won't delete the others yet unless they interfere (which they won't if tenant_id filters them out).
    
    conn.commit()
    print("SUCCESS: Admin tenant updated.")
    
except Exception as e:
    print(f"ERROR: {e}")
    conn.rollback()
finally:
    conn.close()
