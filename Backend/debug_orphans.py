
import sqlite3

def check_orphans():
    conn = sqlite3.connect("sql_app.db")
    cursor = conn.cursor()
    
    print("Checking for ISO 27001 Controls without Process Mapping...")
    
    # Get ISO Framework ID
    cursor.execute("SELECT id FROM frameworks WHERE code LIKE '%ISO27001%'")
    fw = cursor.fetchone()
    if not fw:
        print("ISO 27001 Framework not found!")
        return
    iso_id = fw[0]
    
    # Find active controls for this framework that are NOT in mapping table
    query = """
        SELECT c.id, c.control_id, c.title
        FROM controls c
        WHERE c.framework_id = ?
        AND c.id NOT IN (SELECT control_id FROM process_control_mapping)
    """
    cursor.execute(query, (iso_id,))
    orphans = cursor.fetchall()
    
    print(f"Found {len(orphans)} Orphaned ISO Controls.")
    for o in orphans[:10]: # Show first 10
        print(f" - {o[1]}: {o[2]}")
        
    # Check total counts
    cursor.execute("SELECT count(*) FROM controls WHERE framework_id = ?", (iso_id,))
    total_iso = cursor.fetchone()[0]
    print(f"Total ISO Controls in DB: {total_iso}")
    
    conn.close()

if __name__ == "__main__":
    check_orphans()
