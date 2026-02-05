"""
Complete diagnostic of current database state
"""

import sqlite3

DB_PATH = "sql_app.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("COMPLETE DIAGNOSTIC")
    print("=" * 80)
    
    # 1. Total controls
    cursor.execute("SELECT COUNT(*) FROM controls WHERE framework_id = 13")
    total = cursor.fetchone()[0]
    print(f"\n1. Total controls in database: {total}")
    
    # 2. Mapped controls
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
    mapped = cursor.fetchone()[0]
    print(f"2. Mapped controls: {mapped}/123")
    
    # 3. Unmapped controls
    cursor.execute("""
        SELECT c.control_id, c.title
        FROM controls c
        WHERE c.framework_id = 13
        AND NOT EXISTS (
            SELECT 1 
            FROM intent_framework_crosswalk ifc
            JOIN universal_intents ui ON ui.id = ifc.intent_id
            WHERE (ifc.control_reference = c.control_id OR ifc.control_reference = 'ISO_' || c.control_id)
            AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
            AND ui.category IN (SELECT name FROM processes WHERE framework_code = 'ISO27001')
        )
        ORDER BY c.control_id
    """)
    
    unmapped = cursor.fetchall()
    print(f"3. Unmapped controls: {len(unmapped)}")
    if unmapped:
        for ctrl_id, title in unmapped:
            print(f"   ❌ {ctrl_id}: {title}")
    
    # 4. Check 6.3 specifically
    print(f"\n4. Detailed check of control 6.3:")
    
    # Does 6.3 exist?
    cursor.execute("SELECT control_id, title FROM controls WHERE framework_id=13 AND control_id='6.3'")
    c63 = cursor.fetchone()
    if c63:
        print(f"   ✅ Control exists: {c63[0]} - {c63[1]}")
    else:
        print(f"   ❌ Control 6.3 does NOT exist in database")
    
    # Check crosswalks for 6.3
    cursor.execute("""
        SELECT ifc.id, ifc.intent_id, ifc.control_reference
        FROM intent_framework_crosswalk ifc
        WHERE (ifc.control_reference = '6.3' OR ifc.control_reference = 'ISO_6.3')
        AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
    """)
    crosswalks_63 = cursor.fetchall()
    
    print(f"\n   Crosswalk entries for 6.3: {len(crosswalks_63)}")
    if crosswalks_63:
        for cw_id, intent_id, ctrl_ref in crosswalks_63:
            # Get intent details
            cursor.execute("SELECT category, description FROM universal_intents WHERE id=?", (intent_id,))
            intent = cursor.fetchone()
            if intent:
                print(f"   - Crosswalk {cw_id}: intent {intent_id} ('{intent[0]}') -> {ctrl_ref}")
            else:
                print(f"   - Crosswalk {cw_id}: intent {intent_id} (NOT FOUND) -> {ctrl_ref}")
    else:
        print(f"   ❌ NO crosswalk entries for 6.3!")
    
    # 5. Check for duplicates
    cursor.execute("""
        SELECT c.control_id, COUNT(DISTINCT ui.category) as count, 
               GROUP_CONCAT(DISTINCT ui.category) as categories
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
    """)
    
    duplicates = cursor.fetchall()
    print(f"\n5. Duplicate mappings: {len(duplicates)}")
    if duplicates:
        for ctrl_id, count, cats in duplicates:
            print(f"   ❌ {ctrl_id} in {count} processes: {cats}")
    
    # 6. Check process names
    print(f"\n6. Process names:")
    cursor.execute("SELECT id, name FROM processes WHERE framework_code='ISO27001' ORDER BY name")
    processes = cursor.fetchall()
    for proc_id, name in processes:
        print(f"   {proc_id}: '{name}'")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\nTotal: {total}/123")
    print(f"Mapped: {mapped}/123")
    print(f"Unmapped: {len(unmapped)}")
    print(f"Duplicates: {len(duplicates)}")
    
    return 0

if __name__ == "__main__":
    exit(main())
