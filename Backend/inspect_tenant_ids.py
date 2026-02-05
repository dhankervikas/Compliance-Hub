import sqlite3
import os

DB_PATH = "compliance_restore.db" 
# Note: restoration script used 'compliance_restore.db'? 
# Let me check restore_master_state.py again for the exact DB name.
# It used 'current_compliance.db' usually or 'app.db'. 
# Let's find the actual database file first.

# Check common names
actual_db = "sql_app.db"

if os.path.exists("sql_app.db"):
    actual_db = "sql_app.db"

print(f"Connecting to {actual_db}...")

try:
    conn = sqlite3.connect(actual_db)
    cursor = conn.cursor()

    print("\n--- USERS ---")
    cursor.execute("SELECT id, username, tenant_id FROM users")
    users = cursor.fetchall()
    for u in users:
        print(f"User: {u[1]} (ID: {u[0]}) | Tenant: {u[2]}")

    print("\n--- FRAMEWORKS ---")
    cursor.execute("SELECT id, name, code FROM frameworks")
    fws = cursor.fetchall()
    for f in fws:
        print(f"Framework: {f[1]} (ID: {f[0]}, Code: {f[2]})")

    print("\n--- CONTROLS SAMPLE (First 5) ---")
    cursor.execute("SELECT id, control_id, tenant_id, framework_id FROM controls LIMIT 5")
    ctrls = cursor.fetchall()
    for c in ctrls:
        print(f"Control: {c[1]} (ID: {c[0]}) | Tenant: {c[2]} | FrameworkID: {c[3]}")

    print("\n--- CONTROLS COUNT BY TENANT ---")
    cursor.execute("SELECT tenant_id, COUNT(*) FROM controls GROUP BY tenant_id")
    counts = cursor.fetchall()
    for c in counts:
        print(f"Tenant: {c[0]} | Count: {c[1]}")

    conn.close()
except Exception as e:
    print(e)
