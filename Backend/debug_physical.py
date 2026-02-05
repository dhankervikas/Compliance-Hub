
import sqlite3

DB_PATH = "sql_app.db"

def inspect_physical():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n--- Examining Physical Security (Sample) ---")
    cursor.execute("SELECT id, name FROM processes WHERE name LIKE '%Physical%'")
    p = cursor.fetchone()
    
    if p:
        proc_id = p[0]
        proc_name = p[1]
        print(f"Process: {proc_name} (ID: {proc_id})")
        
        cursor.execute("SELECT id, name FROM sub_processes WHERE process_id = ?", (proc_id,))
        sub_procs = cursor.fetchall()
        
        for sp in sub_procs:
            sp_id = sp[0]
            sp_name = sp[1]
            
            # Join with controls
            query = """
                SELECT c.control_id, c.title, c.category 
                FROM process_control_mapping pcm
                JOIN controls c ON c.id = pcm.control_id
                WHERE pcm.subprocess_id = ?
            """
            cursor.execute(query, (sp_id,))
            controls = cursor.fetchall()
            
            if controls:
                 print(f"  SubProcess: {sp_name} (ID: {sp_id}) - {len(controls)} Controls")
                 for c in controls:
                    print(f"    - [{c[0]}] {c[1]}")
    else:
        print("Process not found!")

    conn.close()

if __name__ == "__main__":
    inspect_physical()
