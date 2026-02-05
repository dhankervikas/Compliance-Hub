
import sqlite3

def repair_subprocesses():
    conn = sqlite3.connect("sql_app.db")
    cursor = conn.cursor()
    
    print("Checking for Processes without SubProcesses...")
    
    # Find empty processes
    cursor.execute("""
        SELECT p.id, p.name 
        FROM processes p 
        LEFT JOIN sub_processes sp ON p.id = sp.process_id 
        WHERE sp.id IS NULL
    """)
    empty_procs = cursor.fetchall()
    
    if not empty_procs:
        print("All processes have at least one SubProcess.")
        return

    print(f"Found {len(empty_procs)} empty processes. Creating defaults...")
    
    new_sps = []
    for pid, pname in empty_procs:
        print(f" - Fixing '{pname}' (ID: {pid})")
        # Create a default intent
        intent_name = f"{pname} Program"
        desc = f"Main policy intent for {pname}"
        new_sps.append((intent_name, desc, pid))
        
    cursor.executemany("INSERT INTO sub_processes (name, description, process_id) VALUES (?, ?, ?)", new_sps)
    conn.commit()
    print(f"Created {len(new_sps)} new SubProcesses.")
    conn.close()

if __name__ == "__main__":
    repair_subprocesses()
