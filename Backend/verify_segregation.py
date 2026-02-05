
import requests
import json

# Testing against local backend
API_URL = "http://localhost:8000/api/v1"

# We need a token. Using a known test user creds or just assuming we can get one?
# Since we are an agent, we can't easily login without knowing raw password of 'admin_legacy' unless we reset it.
# Alternative: Use "run_command" to execute a python script that imports app.api.processes directly?
# Direct DB/Function call is better than HTTP loopback if we don't have token handy.
# BUT `get_processes` depends on `db` and `current_user`.
# Let's mock them in a script that imports 'app'.

import sys
import os

# Mocking dependecies to call the function directly is hard.
# Checking via HTTP is best if we have a token.
# User mentioned "admin_legacy" user. I can try to login as them?
# Or just trust the code reasoning?
# "Run `verify_segregation.py`" was in the plan.

# Let's write a script that queries the DB directly to see 'process_control_mapping'
# And checks if we have controls from DIFFERENT frameworks mapped to same subprocess.

import sqlite3

def check_mixed_mapping():
    conn = sqlite3.connect("sql_app.db")
    cursor = conn.cursor()
    
    print("Checking for Mixed Framework Mappings in 'Risk Management'...")
    
    # 1. Get Risk Management SubProcesses
    cursor.execute("SELECT sp.id, sp.name FROM sub_processes sp JOIN processes p ON p.id = sp.process_id WHERE p.name LIKE '%Risk Management%'")
    subprocs = cursor.fetchall()
    
    for sp_id, sp_name in subprocs:
        print(f"\nSubProcess: {sp_name} (ID: {sp_id})")
        
        # 2. Get Mapped Controls and their Frameworks
        query = """
            SELECT c.control_id, f.code 
            FROM process_control_mapping pcm
            JOIN controls c ON c.id = pcm.control_id
            JOIN frameworks f ON f.id = c.framework_id
            WHERE pcm.subprocess_id = ?
        """
        cursor.execute(query, (sp_id,))
        results = cursor.fetchall()
        
        iso_count = sum(1 for r in results if 'ISO' in r[1])
        nist_count = sum(1 for r in results if 'NIST' in r[1])
        soc2_count = sum(1 for r in results if 'SOC' in r[1])
        
        print(f"  Total Controls: {len(results)}")
        print(f"  ISO Controls: {iso_count}")
        print(f"  NIST Controls: {nist_count}")
        print(f"  SOC2 Controls: {soc2_count}")
        
        if (iso_count > 0 and nist_count > 0) or (iso_count > 0 and soc2_count > 0):
             print("  [WARN] Mixed Frameworks found in DB Mapping! (This confirms need for API filtering)")
        else:
             print("  [INFO] No mixing found in DB (Clean mapping so far)")

    conn.close()

if __name__ == "__main__":
    check_mixed_mapping()
