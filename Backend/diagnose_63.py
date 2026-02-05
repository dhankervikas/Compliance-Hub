"""
Diagnose exactly why 6.3 is not mapping
"""

import sqlite3

DB_PATH = "sql_app.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("DIAGNOSTIC: Why is 6.3 unmapped?")
    print("=" * 80)
    
    # Step 1: Check if control 6.3 exists
    print("\n1. Checking if control 6.3 exists...")
    cursor.execute("""
        SELECT control_id, title, framework_id
        FROM controls
        WHERE control_id = '6.3' AND framework_id = 13
    """)
    
    ctrl = cursor.fetchone()
    if ctrl:
        print(f"   ✅ Control exists: {ctrl[0]} - {ctrl[1]}")
    else:
        print(f"   ❌ Control 6.3 does NOT exist in database!")
        conn.close()
        return
    
    # Step 2: Check all processes
    print("\n2. All ISO27001 processes:")
    cursor.execute("""
        SELECT id, name FROM processes 
        WHERE framework_code = 'ISO27001'
        ORDER BY name
    """)
    
    processes = cursor.fetchall()
    for proc_id, name in processes:
        print(f"   {proc_id:3}. '{name}' (length: {len(name)})")
    
    # Step 3: Check crosswalk entries for 6.3
    print("\n3. Checking crosswalk entries for 6.3...")
    cursor.execute("""
        SELECT ifc.id, ifc.intent_id, ifc.control_reference, ifc.framework_id
        FROM intent_framework_crosswalk ifc
        WHERE (ifc.control_reference = '6.3' OR ifc.control_reference = 'ISO_6.3')
        AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
    """)
    
    crosswalks = cursor.fetchall()
    if crosswalks:
        print(f"   Found {len(crosswalks)} crosswalk entries:")
        for c_id, i_id, ctrl_ref, fw_id in crosswalks:
            print(f"      Crosswalk {c_id}: intent_id={i_id}, control_ref='{ctrl_ref}', framework='{fw_id}'")
            
            # Check the intent
            cursor.execute("""
                SELECT id, category, description
                FROM universal_intents
                WHERE id = ?
            """, (i_id,))
            
            intent = cursor.fetchone()
            if intent:
                print(f"         Intent: category='{intent[1]}', desc='{intent[2][:50]}...'")
            else:
                print(f"         ❌ Intent {i_id} does NOT exist!")
    else:
        print(f"   ❌ NO crosswalk entries found for 6.3")
    
    # Step 4: Check if any intents have category matching Governance process
    print("\n4. Checking intents with 'Governance' category...")
    cursor.execute("""
        SELECT id, category, description
        FROM universal_intents
        WHERE category LIKE '%Govern%'
        LIMIT 5
    """)
    
    gov_intents = cursor.fetchall()
    if gov_intents:
        print(f"   Found {len(gov_intents)} intents with Governance category:")
        for i_id, cat, desc in gov_intents:
            print(f"      Intent {i_id}: '{cat}' - {desc[:40]}...")
    
    # Step 5: Run the exact query that checks for unmapped
    print("\n5. Running unmapped query for 6.3...")
    cursor.execute("""
        SELECT 
            CASE 
                WHEN EXISTS (
                    SELECT 1 
                    FROM intent_framework_crosswalk ifc
                    WHERE (ifc.control_reference = '6.3' OR ifc.control_reference = 'ISO_6.3')
                    AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
                ) THEN 'Has crosswalks'
                ELSE 'No crosswalks'
            END as crosswalk_status,
            
            CASE 
                WHEN EXISTS (
                    SELECT 1 
                    FROM intent_framework_crosswalk ifc
                    JOIN universal_intents ui ON ui.id = ifc.intent_id
                    WHERE (ifc.control_reference = '6.3' OR ifc.control_reference = 'ISO_6.3')
                    AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
                ) THEN 'Intents exist'
                ELSE 'No intents'
            END as intent_status,
            
            CASE 
                WHEN EXISTS (
                    SELECT 1 
                    FROM intent_framework_crosswalk ifc
                    JOIN universal_intents ui ON ui.id = ifc.intent_id
                    WHERE (ifc.control_reference = '6.3' OR ifc.control_reference = 'ISO_6.3')
                    AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
                    AND ui.category IN (SELECT name FROM processes WHERE framework_code = 'ISO27001')
                ) THEN 'Category matches process'
                ELSE 'Category does NOT match'
            END as category_match
    """)
    
    status = cursor.fetchone()
    print(f"   Status: {status[0]} | {status[1]} | {status[2]}")
    
    # Step 6: If category doesn't match, find out why
    if status[2] == 'Category does NOT match':
        print("\n6. Finding category mismatch...")
        cursor.execute("""
            SELECT DISTINCT ui.category
            FROM intent_framework_crosswalk ifc
            JOIN universal_intents ui ON ui.id = ifc.intent_id
            WHERE (ifc.control_reference = '6.3' OR ifc.control_reference = 'ISO_6.3')
            AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
        """)
        
        cats = cursor.fetchall()
        if cats:
            print(f"   Intent categories for 6.3:")
            for cat in cats:
                print(f"      '{cat[0]}'")
            
            # Check if this category exists as a process
            for cat in cats:
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM processes
                    WHERE framework_code = 'ISO27001'
                    AND name = ?
                """, (cat[0],))
                
                exists = cursor.fetchone()[0]
                if exists:
                    print(f"      ✅ '{cat[0]}' EXISTS as a process")
                else:
                    print(f"      ❌ '{cat[0]}' does NOT exist as a process")
                    
                    # Find close matches
                    cursor.execute("""
                        SELECT name
                        FROM processes
                        WHERE framework_code = 'ISO27001'
                        AND name LIKE ?
                    """, (f"%{cat[0][:10]}%",))
                    
                    similar = cursor.fetchall()
                    if similar:
                        print(f"         Similar process names:")
                        for s in similar:
                            print(f"            - '{s[0]}'")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("DIAGNOSIS COMPLETE")
    print("=" * 80)
    
    return 0

if __name__ == "__main__":
    exit(main())
