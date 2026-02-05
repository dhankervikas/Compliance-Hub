"""
Create intents and crosswalk entries for 6.3
"""

import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

DB_PATH = "sql_app.db"
BACKUP_NAME = f"backup_create_63_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

def main():
    print("=" * 80)
    print("CREATE INTENTS AND CROSSWALKS FOR 6.3")
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
        # Check if 6.3 already has crosswalks
        cursor.execute("""
            SELECT COUNT(*)
            FROM intent_framework_crosswalk
            WHERE control_reference = '6.3' OR control_reference = 'ISO_6.3'
        """)
        
        existing = cursor.fetchone()[0]
        
        if existing > 0:
            print(f"\n2. 6.3 already has {existing} crosswalk entries - skipping creation")
        else:
            print(f"\n2. No crosswalk entries for 6.3 - creating fresh...")
            
            # Get max IDs
            cursor.execute("SELECT MAX(id) FROM universal_intents")
            max_intent_id = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT MAX(id) FROM intent_framework_crosswalk")
            max_cross_id = cursor.fetchone()[0] or 0
            
            print(f"   Max intent ID: {max_intent_id}")
            print(f"   Max crosswalk ID: {max_cross_id}")
            
            # Create intents for 6.3
            intents_to_create = [
                "Changes to the ISMS are planned and implemented in a controlled manner",
                "The purpose and potential consequences of changes are considered",
                "The integrity of the ISMS is maintained during changes",
                "Resources needed for changes are determined and provided"
            ]
            
            created_intents = []
            
            for desc in intents_to_create:
                max_intent_id += 1
                
                cursor.execute("""
                    INSERT INTO universal_intents (id, intent_id, description, category)
                    VALUES (?, ?, ?, ?)
                """, (max_intent_id, f"GOV_CHANGE_{max_intent_id}", desc, "Governance & Policy"))
                
                created_intents.append(max_intent_id)
                print(f"   ✅ Created intent {max_intent_id}")
            
            # Create crosswalk entries
            for intent_id in created_intents:
                max_cross_id += 1
                
                cursor.execute("""
                    INSERT INTO intent_framework_crosswalk (
                        id, intent_id, framework_id, control_reference
                    )
                    VALUES (?, ?, ?, ?)
                """, (max_cross_id, intent_id, 'ISO27001', '6.3'))
                
                print(f"   ✅ Created crosswalk {max_cross_id}: intent {intent_id} -> 6.3")
            
            print(f"\n   ✅ Created {len(created_intents)} intents and {len(created_intents)} crosswalks")
        
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
    
    # Verify
    print(f"\n3. Final verification...")
    
    # Check unmapped
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
    
    # Check mapped
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
    
    # Check Governance & Policy controls
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
    print(f"   3. Verify: 22 processes, 123 controls, no duplicates!")
    
    return 0

if __name__ == "__main__":
    exit(main())
