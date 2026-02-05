
import sqlite3

def fix_duplicates():
    conn = sqlite3.connect('sql_app.db')
    cursor = conn.cursor()
    
    print("--- FIXING DUPLICATES ---")

    # 1. Consolidate 'Human Resources Security' -> 'HR Security'
    # Find ID of HR Security
    cursor.execute("SELECT id FROM universal_intents WHERE category = 'HR Security' LIMIT 1")
    hr_sec = cursor.fetchone()
    
    cursor.execute("SELECT id FROM universal_intents WHERE category = 'Human Resources Security' LIMIT 1")
    human_res = cursor.fetchone()

    if hr_sec and human_res:
        print(f"Merging 'Human Resources Security' (ID {human_res[0]}) into 'HR Security' (ID {hr_sec[0]})...")
        # Update mappings
        cursor.execute("UPDATE intent_framework_crosswalk SET intent_id = ? WHERE intent_id = ?", (hr_sec[0], human_res[0]))
        # Delete old intent
        cursor.execute("DELETE FROM universal_intents WHERE id = ?", (human_res[0],))
        print("Merge complete.")
    
    # 2. Fix A.8.14 (Redundancy) -> Keep 'Incident & Resilience', remove 'Backup Management'
    # Intent IDs will differ, so we find the Crosswalk entry for A.8.14 + Backup Management
    # Actually, simpler: Determine which intent ID corresponds to 'Backup Management'
    
    cursor.execute("SELECT id FROM universal_intents WHERE category = 'Backup Management'")
    backup_ids = [r[0] for r in cursor.fetchall()]
    
    if backup_ids:
        placeholders = ','.join('?' for _ in backup_ids)
        # Delete crosswalk for A.8.14 linked to Backup Management
        cursor.execute(f"DELETE FROM intent_framework_crosswalk WHERE control_reference = 'A.8.14' AND intent_id IN ({placeholders})", backup_ids)
        print("Fixed A.8.14 (Removed from Backup Management)")

    # 3. Fix A.8.32 (Change Management) -> Keep 'SDLC (Development)', remove 'Configuration Management'
    cursor.execute("SELECT id FROM universal_intents WHERE category = 'Configuration Management'")
    config_ids = [r[0] for r in cursor.fetchall()]

    if config_ids:
        placeholders = ','.join('?' for _ in config_ids)
        cursor.execute(f"DELETE FROM intent_framework_crosswalk WHERE control_reference = 'A.8.32' AND intent_id IN ({placeholders})", config_ids)
        print("Fixed A.8.32 (Removed from Configuration Management)")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    fix_duplicates()
