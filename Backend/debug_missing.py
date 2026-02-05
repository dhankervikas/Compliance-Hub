
import sqlite3

DB_PATH = "sql_app.db"

def check_missing_processes():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check Threat Intel (18), Legal (19), AI Strat (24)
    target_ids = [18, 19, 24]
    
    print(f"{'Process':<25} | {'SubProc ID'} | {'Controls Mapped'}")
    print("-" * 60)
    
    for pid in target_ids:
        # Get Name
        cursor.execute("SELECT name FROM processes WHERE id = ?", (pid,))
        pname = cursor.fetchone()[0]
        
        # Get SubProcs
        cursor.execute("SELECT id, name FROM sub_processes WHERE process_id = ?", (pid,))
        subprocs = cursor.fetchall()
        
        for sp_id, sp_name in subprocs:
            cursor.execute("SELECT count(*) FROM process_control_mapping WHERE subprocess_id = ?", (sp_id,))
            count = cursor.fetchone()[0]
            print(f"{pname:<25} | {sp_id:<10} | {count}")
            
            if count > 0:
                 cursor.execute("""
                    SELECT c.control_id FROM process_control_mapping pcm 
                    JOIN controls c ON c.id = pcm.control_id 
                    WHERE pcm.subprocess_id = ? LIMIT 3
                 """, (sp_id,))
                 examples = [r[0] for r in cursor.fetchall()]
                 print(f"   Examples: {examples}")

    # Check Control Codes for AI
    print("\n--- AI Control Code Sample ---")
    cursor.execute("SELECT control_id, category FROM controls WHERE control_id LIKE 'ISO42001%' LIMIT 5")
    for r in cursor.fetchall():
        print(f"{r[0]} ({r[1]})")

    conn.close()

if __name__ == "__main__":
    check_missing_processes()
