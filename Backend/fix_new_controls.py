"""
Fix missing fields in newly added controls
Set priority and is_applicable for 9.2.1, 9.2.2, 9.3.1, 9.3.2, 9.3.3
"""

import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

DB_PATH = "sql_app.db"
BACKUP_NAME = f"backup_fix_new_controls_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

def main():
    print("=" * 80)
    print("FIX NEW CONTROLS - Set Missing Required Fields")
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
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Update the 5 new controls with missing fields
        print(f"\n2. Updating new controls with required fields...")
        
        new_controls = ['9.2.1', '9.2.2', '9.3.1', '9.3.2', '9.3.3']
        
        cursor.execute("""
            UPDATE controls
            SET priority = 'medium',
                is_applicable = 1
            WHERE framework_id = 13
            AND control_id IN ('9.2.1', '9.2.2', '9.3.1', '9.3.2', '9.3.3')
            AND (priority IS NULL OR is_applicable IS NULL)
        """)
        
        updated = cursor.rowcount
        print(f"   ✅ Updated {updated} controls")
        
        # Verify the fix
        print(f"\n3. Verifying all controls have required fields...")
        
        cursor.execute("""
            SELECT control_id, priority, is_applicable
            FROM controls
            WHERE framework_id = 13
            AND (priority IS NULL OR is_applicable IS NULL)
        """)
        
        missing = cursor.fetchall()
        
        if missing:
            print(f"\n   ⚠️  Found {len(missing)} controls still missing fields:")
            for ctrl_id, priority, is_applicable in missing:
                print(f"      {ctrl_id}: priority={priority}, is_applicable={is_applicable}")
            
            # Fix them all
            print(f"\n   Fixing all controls with missing fields...")
            cursor.execute("""
                UPDATE controls
                SET priority = COALESCE(priority, 'medium'),
                    is_applicable = COALESCE(is_applicable, 1)
                WHERE framework_id = 13
                AND (priority IS NULL OR is_applicable IS NULL)
            """)
            
            fixed = cursor.rowcount
            print(f"   ✅ Fixed {fixed} additional controls")
        else:
            print(f"   ✅ All controls have required fields!")
        
        # Commit changes
        conn.commit()
        print(f"\n   ✅ All changes committed to database")
        
    except Exception as e:
        print(f"\n   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        print(f"   ⚠️  Changes rolled back")
        conn.close()
        return 1
    
    # Final check
    print(f"\n4. Final verification...")
    
    cursor.execute("""
        SELECT control_id, priority, is_applicable
        FROM controls
        WHERE framework_id = 13
        AND control_id IN ('9.2.1', '9.2.2', '9.3.1', '9.3.2', '9.3.3')
    """)
    
    controls = cursor.fetchall()
    
    print(f"\n   New controls status:")
    for ctrl_id, priority, is_applicable in controls:
        marker = "✅" if priority and is_applicable is not None else "❌"
        print(f"   {marker} {ctrl_id}: priority={priority}, is_applicable={is_applicable}")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("FIX COMPLETE")
    print("=" * 80)
    print(f"\n✅ Backup saved as: {BACKUP_NAME}")
    print(f"✅ All controls now have required fields")
    print(f"\n🔄 Next step: Restart backend and check frontend")
    
    return 0

if __name__ == "__main__":
    exit(main())
