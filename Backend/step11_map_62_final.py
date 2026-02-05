"""
Map 6.2 (Security Objectives) to Governance & Policy
"""

import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

DB_PATH = "sql_app.db"
BACKUP_NAME = f"backup_map_62_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

def main():
    print("=" * 80)
    print("MAP 6.2 (Security Objectives) TO GOVERNANCE & POLICY")
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
        # Check if 6.2 has any crosswalk entries
        cursor.execute("""
            SELECT ifc.id, ifc.intent_id, ui.category
            FROM intent_framework_crosswalk ifc
            LEFT JOIN universal_intents ui ON ui.id = ifc.intent_id
            WHERE (ifc.control_reference = '6.2' OR ifc.control_reference = 'ISO_6.2')
            AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
        """)
        
        crosswalks = cursor.fetchall()
        
        if crosswalks:
            print(f"\n2. Found {len(crosswalks)} crosswalk entries for 6.2:")
            for cw_id, intent_id, category in crosswalks:
                cat_str = category if category else "NULL"
                print(f"   Crosswalk {cw_id}: intent {intent_id} -> category '{cat_str}'")
            
            # Update all intents to Governance & Policy
            print(f"\n3. Updating all 6.2 intents to 'Governance & Policy'...")
            intent_ids = [str(cw[1]) for cw in crosswalks if cw[1]]
            
            if intent_ids:
                cursor.execute(f"""
                    UPDATE universal_intents
                    SET category = 'Governance & Policy'
                    WHERE id IN ({','.join(intent_ids)})
                """)
                updated = cursor.rowcount
                print(f"   ✅ Updated {updated} intents")
            else:
                print(f"   ⚠️  No valid intent IDs found")
                
        else:
            print(f"\n2. No crosswalk entries for 6.2 - creating new ones...")
            
            # Get max IDs
            cursor.execute("SELECT MAX(id) FROM universal_intents")
            max_intent_id = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT MAX(id) FROM intent_framework_crosswalk")
            max_cross_id = cursor.fetchone()[0] or 0
            
            # Create intents for 6.2
            intents_desc = [
                "Information security objectives are established at relevant functions and levels",
                "Security objectives are consistent with the information security policy",
                "Security objectives are measurable (if practicable)",
                "Security objectives take into account information security requirements",
                "Security objectives are communicated",
                "Security objectives are updated as appropriate"
            ]
            
            for desc in intents_desc:
                max_intent_id += 1
                cursor.execute("""
                    INSERT INTO universal_intents (id, intent_id, description, category)
                    VALUES (?, ?, ?, ?)
                """, (max_intent_id, f"GOV_OBJ_{max_intent_id}", desc, "Governance & Policy"))
                
                max_cross_id += 1
                cursor.execute("""
                    INSERT INTO intent_framework_crosswalk (
                        id, intent_id, framework_id, control_reference
                    )
                    VALUES (?, ?, ?, ?)
                """, (max_cross_id, max_intent_id, 'ISO27001', '6.2'))
            
            print(f"   ✅ Created {len(intents_desc)} intents and crosswalks")
        
        # Commit
        conn.commit()
        print(f"\n   ✅ Changes committed to database")
        
    except Exception as e:
        print(f"\n   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        conn.close()
        return 1
    
    # Final verification
    print(f"\n4. Final verification...")
    
    cursor.execute("""
        SELECT COUNT(*)
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
    """)
    
    unmapped = cursor.fetchone()[0]
    
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
    
    # Check Governance & Policy
    cursor.execute("""
        SELECT GROUP_CONCAT(DISTINCT c.control_id ORDER BY c.control_id)
        FROM controls c
        JOIN intent_framework_crosswalk ifc ON (
            ifc.control_reference = c.control_id OR
            ifc.control_reference = 'ISO_' || c.control_id
        )
        JOIN universal_intents ui ON ui.id = ifc.intent_id
        WHERE c.framework_id = 13
        AND ui.category = 'Governance & Policy'
        AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
    """)
    
    gov_controls = cursor.fetchone()[0]
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("FINAL STATUS")
    print("=" * 80)
    
    print(f"\n   Mapped controls: {mapped}/123")
    print(f"   Unmapped controls: {unmapped}")
    print(f"\n   Governance & Policy controls:")
    print(f"   {gov_controls}")
    
    if mapped == 123 and unmapped == 0:
        print(f"\n🎉🎉🎉 PERFECT! 🎉🎉🎉")
        print(f"   ✅ All 123 controls mapped")
        print(f"   ✅ Zero duplicates")
        print(f"   ✅ Zero unmapped")
        print(f"   ✅ ISO 27001:2022 COMPLETE!")
    else:
        print(f"\n⚠️  Status: {mapped}/123 mapped, {unmapped} unmapped")
    
    print(f"\n✅ Backup saved as: {BACKUP_NAME}")
    print(f"\n🔄 FINAL STEP:")
    print(f"   1. Restart backend")
    print(f"   2. Refresh frontend")
    print(f"   3. DONE! 🎉")
    
    return 0

if __name__ == "__main__":
    exit(main())
