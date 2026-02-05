"""
FORCE REMOVE DUPLICATES
Delete crosswalk entries for controls that appear in multiple processes
Keep only the correct process for each control
"""

import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

DB_PATH = "sql_app.db"
BACKUP_NAME = f"backup_remove_duplicates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

def main():
    print("=" * 80)
    print("FORCE REMOVE DUPLICATE MAPPINGS")
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
    
    # Define which duplicates to remove and from where
    duplicates_to_fix = [
        # (control_id, remove_from_category, keep_in_category)
        ('6.1.2', 'Threat Intel', 'Risk Management'),
        ('8.2', 'Access Control (IAM)', 'Risk Management'),
        ('8.3', 'Access Control (IAM)', 'Risk Management'),
        ('A.6.1', 'Risk Management', 'HR Security'),
        ('A.6.7', 'HR Security', 'Access Control (IAM)'),
        ('A.7.1', 'HR Security', 'Physical Security'),
        ('A.7.2', 'HR Security', 'Physical Security'),
        ('A.7.3', 'HR Security', 'Physical Security'),
        ('A.7.4', 'Incident & Resilience', 'Physical Security'),
        ('A.8.1', 'Risk Management', 'Operations'),
        ('6.2', 'HR Security', 'Governance & Policy'),  # Also fix this
    ]
    
    try:
        total_deleted = 0
        
        print(f"\n2. Removing duplicate mappings...")
        
        for ctrl_id, remove_from, keep_in in duplicates_to_fix:
            # Find and delete crosswalk entries that link this control to the wrong category
            cursor.execute("""
                DELETE FROM intent_framework_crosswalk
                WHERE id IN (
                    SELECT ifc.id
                    FROM intent_framework_crosswalk ifc
                    JOIN universal_intents ui ON ui.id = ifc.intent_id
                    WHERE (ifc.control_reference = ? OR ifc.control_reference = 'ISO_' || ?)
                    AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
                    AND ui.category = ?
                )
            """, (ctrl_id, ctrl_id, remove_from))
            
            deleted = cursor.rowcount
            total_deleted += deleted
            
            if deleted > 0:
                print(f"   ✅ Removed {ctrl_id} from '{remove_from}' (keeping in '{keep_in}')")
            else:
                print(f"   ℹ️  {ctrl_id} not found in '{remove_from}'")
        
        # Commit changes
        conn.commit()
        print(f"\n   ✅ Total crosswalk entries deleted: {total_deleted}")
        print(f"   ✅ All changes committed to database")
        
    except Exception as e:
        print(f"\n   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        print(f"   ⚠️  Changes rolled back")
        conn.close()
        return 1
    
    # Verify no more duplicates
    print(f"\n3. Checking for remaining duplicates...")
    
    cursor.execute("""
        SELECT c.control_id, COUNT(DISTINCT ui.category) as process_count, 
               GROUP_CONCAT(DISTINCT ui.category) as processes
        FROM controls c
        JOIN intent_framework_crosswalk ifc ON (
            ifc.control_reference = c.control_id OR
            ifc.control_reference = 'ISO_' || c.control_id
        )
        JOIN universal_intents ui ON ui.id = ifc.intent_id
        WHERE c.framework_id = 13
        AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
        AND ui.category IN (SELECT name FROM processes WHERE framework_code = 'ISO27001')
        GROUP BY c.control_id
        HAVING COUNT(DISTINCT ui.category) > 1
        ORDER BY c.control_id
    """)
    
    duplicates = cursor.fetchall()
    
    if duplicates:
        print(f"\n   ⚠️  Still found {len(duplicates)} duplicates:")
        for ctrl_id, count, processes in duplicates:
            print(f"      {ctrl_id} in {count} processes: {processes}")
    else:
        print(f"\n   ✅ No duplicates found!")
    
    # Check total mapped controls
    cursor.execute("""
        SELECT COUNT(DISTINCT c.id)
        FROM controls c
        JOIN intent_framework_crosswalk ifc ON (
            ifc.control_reference = c.control_id OR
            ifc.control_reference = 'ISO_' || c.control_id
        )
        JOIN universal_intents ui ON ui.id = ifc.intent_id
        WHERE c.framework_id = 13
        AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
        AND ui.category IN (SELECT name FROM processes WHERE framework_code = 'ISO27001')
    """)
    
    mapped_count = cursor.fetchone()[0]
    
    # Verify key processes
    print(f"\n4. Key process verification...")
    
    key_checks = [
        ('HR Security', 'A.6.1-8, 7.1-7.3 clauses'),
        ('Risk Management', '6.1.1-3, 6.2, 8.1-8.3 clauses'),
        ('Access Control (IAM)', 'Should have A.6.7'),
        ('Physical Security', 'A.7.x only'),
        ('Cryptography', 'A.8.11, A.8.12, A.8.24'),
    ]
    
    for proc_name, expected in key_checks:
        cursor.execute("""
            SELECT COUNT(DISTINCT c.control_id), 
                   GROUP_CONCAT(DISTINCT c.control_id ORDER BY c.control_id)
            FROM controls c
            JOIN intent_framework_crosswalk ifc ON (
                ifc.control_reference = c.control_id OR
                ifc.control_reference = 'ISO_' || c.control_id
            )
            JOIN universal_intents ui ON ui.id = ifc.intent_id
            WHERE c.framework_id = 13
            AND ui.category = ?
            AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
        """, (proc_name,))
        
        result = cursor.fetchone()
        count = result[0]
        controls = result[1] if result[1] else "none"
        
        print(f"\n   {proc_name}: {count} controls")
        if count <= 15:
            print(f"      {controls}")
        print(f"      Expected: {expected}")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("FINAL STATUS")
    print("=" * 80)
    
    print(f"\n   Total mapped controls: {mapped_count}/123")
    print(f"   Duplicates: {len(duplicates)}")
    print(f"   Crosswalk entries deleted: {total_deleted}")
    
    if duplicates == [] and mapped_count == 123:
        print(f"\n🎉🎉🎉 PERFECT! 🎉🎉🎉")
        print(f"   ✅ All 123 controls mapped")
        print(f"   ✅ Zero duplicates")
        print(f"   ✅ All mappings correct")
    elif duplicates == []:
        print(f"\n✅ No duplicates!")
        print(f"⚠️  Mapped: {mapped_count}/123")
    else:
        print(f"\n⚠️  Still have {len(duplicates)} duplicates")
    
    print(f"\n✅ Backup saved as: {BACKUP_NAME}")
    print(f"\n🔄 Next step: Restart backend and verify frontend")
    
    return 0

if __name__ == "__main__":
    exit(main())
