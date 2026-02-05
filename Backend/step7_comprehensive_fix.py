"""
COMPREHENSIVE FIX - All Remaining Mapping Issues:
1. Remove A.6.2 from Governance & Policy (keep in HR Security only)
2. Remove 6.1.1 from HR Security (keep in Risk Management only)
3. Remove clauses 7.1, 7.2, 7.3 from Physical Security (keep in HR Security only)
4. Remove clause 7.4 from Physical Security (keep in Incident & Resilience only)
5. Move 8.1 from Operations to Risk Management
6. Move A.8.12 (DLP) from Operations to Cryptography
7. Check for all remaining duplicates
"""

import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

DB_PATH = "sql_app.db"
BACKUP_NAME = f"backup_comprehensive_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

def main():
    print("=" * 80)
    print("COMPREHENSIVE FIX - All Remaining Mapping Issues")
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
        # Fix 1: Remove A.6.2 from Governance & Policy (keep in HR Security)
        print(f"\n2. Removing A.6.2 (Annex A) from Governance & Policy...")
        cursor.execute("""
            UPDATE universal_intents
            SET category = 'HR Security'
            WHERE category = 'Governance & Policy'
            AND id IN (
                SELECT ui.id
                FROM universal_intents ui
                JOIN intent_framework_crosswalk ifc ON ifc.intent_id = ui.id
                WHERE ifc.control_reference = 'A.6.2'
                AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
            )
        """)
        moved_a62 = cursor.rowcount
        print(f"   ✅ Moved {moved_a62} intents for A.6.2 to HR Security")
        
        # Fix 2: Remove 6.1.1 (clause) from HR Security (keep in Risk Management)
        print(f"\n3. Removing 6.1.1 (clause) from HR Security...")
        cursor.execute("""
            UPDATE universal_intents
            SET category = 'Risk Management'
            WHERE category = 'HR Security'
            AND id IN (
                SELECT ui.id
                FROM universal_intents ui
                JOIN intent_framework_crosswalk ifc ON ifc.intent_id = ui.id
                WHERE (ifc.control_reference = '6.1.1' OR ifc.control_reference = 'ISO_6.1.1')
                AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
            )
        """)
        moved_611 = cursor.rowcount
        print(f"   ✅ Moved {moved_611} intents for 6.1.1 to Risk Management")
        
        # Fix 3: Remove clauses 7.1, 7.2, 7.3 from Physical Security (keep in HR Security)
        print(f"\n4. Removing clauses 7.1, 7.2, 7.3 from Physical Security...")
        cursor.execute("""
            UPDATE universal_intents
            SET category = 'HR Security'
            WHERE category = 'Physical Security'
            AND id IN (
                SELECT ui.id
                FROM universal_intents ui
                JOIN intent_framework_crosswalk ifc ON ifc.intent_id = ui.id
                WHERE (
                    ifc.control_reference IN ('7.1', '7.2', '7.3') OR
                    ifc.control_reference IN ('ISO_7.1', 'ISO_7.2', 'ISO_7.3')
                )
                AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
            )
        """)
        moved_71_73 = cursor.rowcount
        print(f"   ✅ Moved {moved_71_73} intents for 7.1, 7.2, 7.3 to HR Security")
        
        # Fix 4: Remove clause 7.4 from Physical Security (keep in Incident & Resilience)
        print(f"\n5. Removing clause 7.4 from Physical Security...")
        cursor.execute("""
            UPDATE universal_intents
            SET category = 'Incident & Resilience'
            WHERE category = 'Physical Security'
            AND id IN (
                SELECT ui.id
                FROM universal_intents ui
                JOIN intent_framework_crosswalk ifc ON ifc.intent_id = ui.id
                WHERE (ifc.control_reference = '7.4' OR ifc.control_reference = 'ISO_7.4')
                AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
            )
        """)
        moved_74 = cursor.rowcount
        print(f"   ✅ Moved {moved_74} intents for 7.4 to Incident & Resilience")
        
        # Fix 5: Move 8.1 from Operations to Risk Management
        print(f"\n6. Moving 8.1 from Operations to Risk Management...")
        cursor.execute("""
            UPDATE universal_intents
            SET category = 'Risk Management'
            WHERE category = 'Operations'
            AND id IN (
                SELECT ui.id
                FROM universal_intents ui
                JOIN intent_framework_crosswalk ifc ON ifc.intent_id = ui.id
                WHERE (ifc.control_reference = '8.1' OR ifc.control_reference = 'ISO_8.1')
                AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
            )
        """)
        moved_81 = cursor.rowcount
        print(f"   ✅ Moved {moved_81} intents for 8.1 to Risk Management")
        
        # Fix 6: Move A.8.12 (DLP) from Operations to Cryptography
        print(f"\n7. Moving A.8.12 (DLP) from Operations to Cryptography...")
        cursor.execute("""
            UPDATE universal_intents
            SET category = 'Cryptography'
            WHERE category = 'Operations'
            AND id IN (
                SELECT ui.id
                FROM universal_intents ui
                JOIN intent_framework_crosswalk ifc ON ifc.intent_id = ui.id
                WHERE ifc.control_reference = 'A.8.12'
                AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
            )
        """)
        moved_a812 = cursor.rowcount
        print(f"   ✅ Moved {moved_a812} intents for A.8.12 to Cryptography")
        
        # Commit all changes
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
    
    # Check for duplicates
    print(f"\n8. Checking for duplicate control mappings...")
    
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
        print(f"\n   ⚠️  Found {len(duplicates)} controls mapped to multiple processes:")
        for ctrl_id, count, processes in duplicates:
            print(f"      {ctrl_id} appears in {count} processes: {processes}")
    else:
        print(f"\n   ✅ No duplicate mappings found!")
    
    # Verify key processes
    print(f"\n9. Final process verification...")
    
    key_processes = [
        ('HR Security', 'A.6.1-8, 7.1, 7.2, 7.3'),
        ('Risk Management', '6.1.1, 6.1.2, 6.1.3, 6.2, 8.1, 8.2, 8.3'),
        ('Governance & Policy', '6.2, 6.3, 7.5.x (no A.6.2)'),
        ('Physical Security', 'A.7.x only (no clauses 7.1-7.4)'),
        ('Incident & Resilience', '7.4 clause'),
        ('Operations', 'No 8.1, No A.8.12'),
        ('Cryptography', 'A.8.11, A.8.24, A.8.12')
    ]
    
    for proc_name, expected in key_processes:
        cursor.execute("""
            SELECT GROUP_CONCAT(DISTINCT c.control_id ORDER BY c.control_id)
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
        controls = result[0] if result and result[0] else "none"
        
        # Count controls
        control_count = len(controls.split(',')) if controls != "none" else 0
        
        print(f"\n   {proc_name}: {control_count} controls")
        if control_count <= 15:  # Only show full list for small sets
            print(f"      Controls: {controls}")
        else:
            # Show first few
            control_list = controls.split(',')
            print(f"      Controls: {', '.join(control_list[:10])}... ({control_count} total)")
        print(f"      Expected: {expected}")
    
    # Final count
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
    
    mapped_controls = cursor.fetchone()[0]
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("FINAL STATUS")
    print("=" * 80)
    
    print(f"\n   Total mapped controls: {mapped_controls}/123")
    print(f"   Duplicate mappings: {len(duplicates)}")
    
    if duplicates == 0 and mapped_controls == 123:
        print(f"\n🎉 PERFECT!")
        print(f"   ✅ All 123 controls mapped")
        print(f"   ✅ No duplicates")
        print(f"   ✅ All mappings correct")
    elif duplicates == 0:
        print(f"\n✅ No duplicates!")
        print(f"⚠️  Mapped controls: {mapped_controls}/123")
    else:
        print(f"\n⚠️  Still have {len(duplicates)} duplicate mappings")
    
    print(f"\n✅ Backup saved as: {BACKUP_NAME}")
    print(f"\n🔄 Next step: Restart backend and check frontend")
    
    return 0

if __name__ == "__main__":
    exit(main())
