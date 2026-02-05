"""
Step 1: Remove 2 Duplicate Processes (24 → 22)
Deletes: "Human Resources Security" and "Access Control"
"""

import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

# Configuration
DB_PATH = "sql_app.db"
BACKUP_NAME = f"backup_step1_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

def main():
    print("=" * 80)
    print("STEP 1: Remove 2 Duplicate Processes")
    print("=" * 80)
    
    # Check if database exists
    if not Path(DB_PATH).exists():
        print(f"\n❌ ERROR: Database '{DB_PATH}' not found!")
        print("   Make sure you're in the Backend directory")
        return 1
    
    # Backup database
    print(f"\n1. Creating backup: {BACKUP_NAME}")
    try:
        shutil.copy2(DB_PATH, BACKUP_NAME)
        print(f"   ✅ Backup created successfully")
    except Exception as e:
        print(f"   ❌ Backup failed: {e}")
        return 1
    
    # Connect to database
    print(f"\n2. Connecting to database...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check current state
    print(f"\n3. Checking current state...")
    cursor.execute("SELECT COUNT(*) FROM processes WHERE framework_code='ISO27001'")
    before_count = cursor.fetchone()[0]
    print(f"   Current ISO27001 processes: {before_count}")
    
    # Check if duplicates exist
    cursor.execute("SELECT id, name FROM processes WHERE id IN (55, 56)")
    duplicates = cursor.fetchall()
    
    if not duplicates:
        print("\n   ⚠️  Duplicates not found (already deleted?)")
        conn.close()
        return 0
    
    print(f"   Found {len(duplicates)} processes to delete:")
    for proc_id, name in duplicates:
        print(f"      - ID {proc_id}: '{name}'")
    
    # Execute deletions
    print(f"\n4. Deleting duplicate processes...")
    try:
        # Delete Human Resources Security
        cursor.execute("""
            DELETE FROM processes 
            WHERE id = 55 
            AND name = 'Human Resources Security'
            AND framework_code = 'ISO27001'
        """)
        print(f"   ✅ Deleted: 'Human Resources Security' (ID 55)")
        
        # Delete Access Control
        cursor.execute("""
            DELETE FROM processes 
            WHERE id = 56 
            AND name = 'Access Control'
            AND framework_code = 'ISO27001'
        """)
        print(f"   ✅ Deleted: 'Access Control' (ID 56)")
        
        # Commit changes
        conn.commit()
        print(f"\n   ✅ Changes committed to database")
        
    except Exception as e:
        print(f"\n   ❌ Error during deletion: {e}")
        conn.rollback()
        print(f"   ⚠️  Changes rolled back")
        conn.close()
        return 1
    
    # Verify final state
    print(f"\n5. Verifying results...")
    cursor.execute("SELECT COUNT(*) FROM processes WHERE framework_code='ISO27001'")
    after_count = cursor.fetchone()[0]
    
    print(f"\n   Before: {before_count} processes")
    print(f"   After:  {after_count} processes")
    print(f"   Deleted: {before_count - after_count} processes")
    
    if after_count == 22:
        print(f"\n   ✅ SUCCESS! Target of 22 processes reached!")
    else:
        print(f"\n   ⚠️  Expected 22 processes, but got {after_count}")
    
    # List remaining processes
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
    print("STEP 1 COMPLETE")
    print("=" * 80)
    print(f"\n✅ Backup saved as: {BACKUP_NAME}")
    print(f"✅ Duplicates removed")
    print(f"✅ Final count: {after_count} processes")
    print(f"\n💡 Next step: Restart your backend to see the changes")
    print(f"   Then run: python step2_fix_mappings.py")
    
    return 0

if __name__ == "__main__":
    exit(main())
