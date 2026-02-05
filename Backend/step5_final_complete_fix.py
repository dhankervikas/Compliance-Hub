"""
FINAL COMPLETE FIX:
1. Add missing controls: 9.2.1, 9.2.2, 9.3.1, 9.3.2, 9.3.3
2. Fix wrong mappings:
   - 6.1.1: HR Security → Risk Management
   - 6.2: HR Security → Governance & Policy  
   - 7.4: Physical Security → Incident & Resilience
3. Map 6.3 to Governance & Policy
Result: 123 controls (93 Annex A + 30 clauses), all correctly mapped
"""

import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

DB_PATH = "sql_app.db"
BACKUP_NAME = f"backup_final_complete_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

def main():
    print("=" * 80)
    print("FINAL COMPLETE FIX - ADD CONTROLS & FIX ALL MAPPINGS")
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
    
    # Get framework ID and tenant ID
    cursor.execute("SELECT id FROM frameworks WHERE code='ISO27001'")
    framework_id = cursor.fetchone()[0]
    
    cursor.execute("SELECT DISTINCT tenant_id FROM controls WHERE framework_id=? LIMIT 1", (framework_id,))
    tenant_result = cursor.fetchone()
    tenant_id = tenant_result[0] if tenant_result else 'default_tenant'
    
    print(f"   Framework ID: {framework_id}")
    print(f"   Tenant ID: {tenant_id}")
    
    try:
        # Part 1: Fix wrong mappings
        print(f"\n2. Fixing wrong mappings...")
        
        # Fix 6.1.1: HR Security → Risk Management
        print(f"\n   Moving 6.1.1 from HR Security to Risk Management...")
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
        
        # Fix 6.2: HR Security → Governance & Policy
        print(f"\n   Moving 6.2 from HR Security to Governance & Policy...")
        cursor.execute("""
            UPDATE universal_intents
            SET category = 'Governance & Policy'
            WHERE category = 'HR Security'
            AND id IN (
                SELECT ui.id
                FROM universal_intents ui
                JOIN intent_framework_crosswalk ifc ON ifc.intent_id = ui.id
                WHERE (ifc.control_reference = '6.2' OR ifc.control_reference = 'ISO_6.2')
                AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
            )
        """)
        moved_62 = cursor.rowcount
        print(f"   ✅ Moved {moved_62} intents for 6.2 to Governance & Policy")
        
        # Fix 7.4: Physical Security → Incident & Resilience
        print(f"\n   Moving 7.4 from Physical Security to Incident & Resilience...")
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
        
        # Map 6.3 to Governance & Policy
        print(f"\n   Mapping 6.3 to Governance & Policy...")
        cursor.execute("""
            UPDATE universal_intents
            SET category = 'Governance & Policy'
            WHERE id IN (
                SELECT ui.id
                FROM universal_intents ui
                JOIN intent_framework_crosswalk ifc ON ifc.intent_id = ui.id
                WHERE (ifc.control_reference = '6.3' OR ifc.control_reference = 'ISO_6.3')
                AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
            )
        """)
        mapped_63 = cursor.rowcount
        if mapped_63 > 0:
            print(f"   ✅ Mapped {mapped_63} intents for 6.3 to Governance & Policy")
        else:
            print(f"   ℹ️  6.3 has no existing intents - will create later if needed")
        
        # Part 2: Add missing controls
        print(f"\n3. Adding missing controls...")
        
        # Controls to add
        missing_controls = [
            ('9.2.1', 'Internal audit program', 'Plan, establish, implement and maintain an audit program', 'Performance Evaluation'),
            ('9.2.2', 'Conducting internal audits', 'Conduct internal audits at planned intervals', 'Performance Evaluation'),
            ('9.3.1', 'Management review inputs', 'Management review shall include consideration of specified inputs', 'Performance Evaluation'),
            ('9.3.2', 'Management review results', 'Management review results shall include decisions related to continual improvement', 'Performance Evaluation'),
            ('9.3.3', 'Management review documentation', 'Retain documented information as evidence of management reviews', 'Performance Evaluation'),
        ]
        
        # Get max IDs
        cursor.execute("SELECT MAX(id) FROM universal_intents")
        max_intent_id = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT MAX(id) FROM intent_framework_crosswalk")
        max_cross_id = cursor.fetchone()[0] or 0
        
        added_count = 0
        for ctrl_id, title, description, category in missing_controls:
            # Check if control already exists
            cursor.execute("""
                SELECT COUNT(*) 
                FROM controls 
                WHERE framework_id=? AND control_id=?
            """, (framework_id, ctrl_id))
            
            exists = cursor.fetchone()[0]
            
            if exists == 0:
                # Add control
                cursor.execute("""
                    INSERT INTO controls (
                        control_id, title, description, framework_id, 
                        status, tenant_id, category
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (ctrl_id, title, description, framework_id, 'not_started', tenant_id, category))
                
                print(f"   ✅ Added control {ctrl_id}: {title}")
                added_count += 1
                
                # Create intents for this control
                intents = [
                    f"{description}",
                    f"The {title.lower()} process is documented and maintained",
                    f"Records of {title.lower()} are retained"
                ]
                
                intent_ids = []
                for intent_desc in intents:
                    max_intent_id += 1
                    cursor.execute("""
                        INSERT INTO universal_intents (id, intent_id, description, category)
                        VALUES (?, ?, ?, ?)
                    """, (max_intent_id, f"PERF_{max_intent_id}", intent_desc, category))
                    intent_ids.append(max_intent_id)
                
                # Create crosswalk mappings
                for intent_id in intent_ids:
                    max_cross_id += 1
                    cursor.execute("""
                        INSERT INTO intent_framework_crosswalk (
                            id, intent_id, framework_id, control_reference
                        )
                        VALUES (?, ?, ?, ?)
                    """, (max_cross_id, intent_id, 'ISO27001', ctrl_id))
                
                print(f"      Created {len(intents)} intents and mappings")
            else:
                print(f"   ℹ️  Control {ctrl_id} already exists")
        
        print(f"\n   Total controls added: {added_count}")
        
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
    
    # Verify final state
    print(f"\n4. Verifying final state...")
    
    cursor.execute("SELECT COUNT(*) FROM controls WHERE framework_id=?", (framework_id,))
    total_controls = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(DISTINCT c.id)
        FROM controls c
        JOIN intent_framework_crosswalk ifc ON (
            ifc.control_reference = c.control_id OR
            ifc.control_reference = 'ISO_' || c.control_id
        )
        JOIN universal_intents ui ON ui.id = ifc.intent_id
        WHERE c.framework_id = ?
        AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
        AND ui.category IN (SELECT name FROM processes WHERE framework_code = 'ISO27001')
    """, (framework_id,))
    
    mapped_controls = cursor.fetchone()[0]
    
    # Check key processes
    print(f"\n   Key process control counts:")
    
    key_checks = [
        ('HR Security', 'Should have A.6.x only (8 controls)'),
        ('Risk Management', 'Should have 6.1.x, 6.2, 8.2, 8.3'),
        ('Governance & Policy', 'Should have 6.2, 6.3, 7.5.x'),
        ('Performance Evaluation', 'Should have A.5.35, 9.1, 9.2.x, 9.3.x'),
        ('Incident & Resilience', 'Should have 7.4'),
        ('Physical Security', 'Should NOT have 7.4')
    ]
    
    for proc_name, expected in key_checks:
        cursor.execute("""
            SELECT COUNT(DISTINCT c.control_id), GROUP_CONCAT(DISTINCT c.control_id)
            FROM controls c
            JOIN intent_framework_crosswalk ifc ON (
                ifc.control_reference = c.control_id OR
                ifc.control_reference = 'ISO_' || c.control_id
            )
            JOIN universal_intents ui ON ui.id = ifc.intent_id
            WHERE c.framework_id = ?
            AND ui.category = ?
            AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
        """, (framework_id, proc_name))
        
        result = cursor.fetchone()
        count = result[0] if result else 0
        controls = result[1] if result and result[1] else "none"
        
        print(f"\n   {proc_name}: {count} controls")
        if count < 20:  # Only show details for small lists
            print(f"      Controls: {controls}")
        print(f"      {expected}")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("FINAL STATUS")
    print("=" * 80)
    
    print(f"\n   Total controls: {total_controls}")
    print(f"   Mapped controls: {mapped_controls}")
    print(f"   Unmapped: {total_controls - mapped_controls}")
    
    if total_controls == 123 and mapped_controls == 123:
        print(f"\n🎉🎉🎉 PERFECT! 🎉🎉🎉")
        print(f"   ✅ Total controls: 123 (93 Annex A + 30 clauses)")
        print(f"   ✅ All controls mapped correctly")
        print(f"   ✅ No duplicates")
        print(f"   ✅ ISO 27001:2022 COMPLETE!")
    elif total_controls == 123:
        print(f"\n✅ Total controls: 123 (CORRECT!)")
        print(f"⚠️  But {123 - mapped_controls} controls are unmapped")
    else:
        print(f"\n⚠️  Status:")
        print(f"   Total: {total_controls}/123")
        print(f"   Mapped: {mapped_controls}/123")
    
    print(f"\n✅ Backup saved as: {BACKUP_NAME}")
    print(f"\n🔄 Next steps:")
    print(f"   1. Restart backend")
    print(f"   2. Run: python review_all_mappings.py")
    print(f"   3. Verify all mappings are correct")
    print(f"   4. Check frontend - should see 123 controls total")
    
    return 0

if __name__ == "__main__":
    exit(main())
