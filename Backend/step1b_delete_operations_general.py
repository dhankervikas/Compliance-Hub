"""
Delete only: ID 36 - Operations (General)
This process has 0 intents and shows 0 controls to users
"""

import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

DB_PATH = "sql_app.db"
BACKUP_NAME = f"backup_delete_ops_general_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

def main():
    print("=" * 80)
    print("DELETE: Operations (General) - ID 36")
    print("=" * 80)
    
    if not Path(DB_PATH).exists():
        print(f"\n❌ ERROR: Database '{DB_PATH}' not found!")
        return 1
    
    # Backup
    print(f"\n1. Creating backup: {BACKUP_NAME}")
    try:
        shutil.copy2(DB_PATH, BACKUP_NAME)
        print(f"   ✅ Backup created successfully")
    except Exception as e:
        print(f"   ❌ Backup failed: {e}")
        return 1
    
    # Connect
    print(f"\n2. Connecting to database...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Current count
    print(f"\n3. Checking current state...")
    cursor.execute("SELECT COUNT(*) FROM processes WHERE framework_code='ISO27001'")
    before = cursor.fetchone()[0]
    print(f"   Current ISO27001 processes: {before}")
    
    # Check if it exists
    cursor.execute("SELECT id, name FROM processes WHERE id=36 AND framework_code='ISO27001'")
    proc = cursor.fetchone()
    
    if not proc:
        print("\n   ⚠️  Process ID 36 not found (already deleted?)")
        conn.close()
        return 0
    
    proc_id, proc_name = proc
    print(f"   Found: ID {proc_id} - '{proc_name}'")
    
    # Check intents
    cursor.execute("SELECT COUNT(*) FROM universal_intents WHERE category=?", (proc_name,))
    intent_count = cursor.fetchone()[0]
    print(f"   Intents: {intent_count} (0 = empty process)")
    
    # Delete it
    print(f"\n4. Deleting process...")
    try:
        cursor.execute("""
            DELETE FROM processes 
            WHERE id = 36 
            AND framework_code = 'ISO27001'
        """)
        conn.commit()
        print(f"   ✅ Deleted: '{proc_name}' (ID {proc_id})")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        conn.rollback()
        conn.close()
        return 1
    
    # Final count
    print(f"\n5. Verifying results...")
    cursor.execute("SELECT COUNT(*) FROM processes WHERE framework_code='ISO27001'")
    after = cursor.fetchone()[0]
    
    print(f"\n   Before: {before} processes")
    print(f"   After:  {after} processes")
    print(f"   Deleted: {before - after} process")
    
    # List remaining
    print(f"\n6. Remaining ISO27001 processes:")
    cursor.execute("""
        SELECT id, name 
        FROM processes 
        WHERE framework_code='ISO27001'
        ORDER BY name
    """)
    
    processes = cursor.fetchall()
    for proc_id, name in processes:
        print(f"   {proc_id:3}. {name}")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("DELETION COMPLETE")
    print("=" * 80)
    print(f"\n✅ Backup saved as: {BACKUP_NAME}")
    print(f"✅ Process deleted: 'Operations (General)' (ID 36)")
    print(f"✅ Database now has: {after} processes")
    print(f"\n💡 Since this process had 0 intents:")
    print(f"   - It was likely already hidden in frontend")
    print(f"   - Frontend should now show: 22 processes ✅")
    print(f"\n🔄 Next steps:")
    print(f"   1. Restart backend to apply changes")
    print(f"   2. Check frontend - should see 22 processes")
    print(f"   3. Then run: python step2_fix_mappings.py")
    
    return 0

if __name__ == "__main__":
    exit(main())
