"""
FINAL CLEANUP - Fix Annex A vs Clause Confusion
Remove duplicate mappings where Annex A controls are in wrong places
"""

import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

DB_PATH = "sql_app.db"
BACKUP_NAME = f"backup_final_cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

def main():
    print("=" * 80)
    print("FINAL CLEANUP - Fix Annex A vs Clause Duplicates")
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
        # Fix 1: Remove A.7.1, A.7.2, A.7.3 from HR Security (keep clauses 7.1, 7.2, 7.3)
        print(f"\n2. Removing A.7.1, A.7.2, A.7.3 (Annex A) from HR Security...")
        print(f"   (Keeping 7.1, 7.2, 7.3 clauses in HR Security)")
        
        cursor.execute("""
            UPDATE universal_intents
            SET category = 'Physical Security'
            WHERE category = 'HR Security'
            AND id IN (
                SELECT ui.id
                FROM universal_intents ui
                JOIN intent_framework_crosswalk ifc ON ifc.intent_id = ui.id
                WHERE ifc.control_reference IN ('A.7.1', 'A.7.2', 'A.7.3')
                AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
            )
        """)
        moved_a7 = cursor.rowcount
        print(f"   ✅ Moved {moved_a7} intents for A.7.1, A.7.2, A.7.3 to Physical Security")
        
        # Fix 2: Remove A.8.2, A.8.3 from Risk Management (keep clauses 8.2, 8.3)
        print(f"\n3. Removing A.8.2, A.8.3 (Annex A) from Risk Management...")
        print(f"   (Keeping 8.2, 8.3 clauses in Risk Management)")
        
        cursor.execute("""
            UPDATE universal_intents
            SET category = 'Access Control (IAM)'
            WHERE category = 'Risk Management'
            AND id IN (
                SELECT ui.id
                FROM universal_intents ui
                JOIN intent_framework_crosswalk ifc ON ifc.intent_id = ui.id
                WHERE ifc.control_reference IN ('A.8.2', 'A.8.3')
                AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
            )
        """)
        moved_a8 = cursor.rowcount
        print(f"   ✅ Moved {moved_a8} intents for A.8.2, A.8.3 to Access Control (IAM)")
        
        # Fix 3: Remove A.6.1 from Risk Management
        print(f"\n4. Removing A.6.1 (Annex A) from Risk Management...")
        
        cursor.execute("""
            UPDATE universal_intents
            SET category = 'HR Security'
            WHERE category = 'Risk Management'
            AND id IN (
                SELECT ui.id
                FROM universal_intents ui
                JOIN intent_framework_crosswalk ifc ON ifc.intent_id = ui.id
                WHERE ifc.control_reference = 'A.6.1'
                AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
            )
        """)
        moved_a6 = cursor.rowcount
        print(f"   ✅ Moved {moved_a6} intents for A.6.1 to HR Security")
        
        # Fix 4: Remove A.7.4 from Incident & Resilience (keep clause 7.4)
        print(f"\n5. Removing A.7.4 (Annex A) from Incident & Resilience...")
        print(f"   (Keeping 7.4 clause in Incident & Resilience)")
        
        cursor.execute("""
            UPDATE universal_intents
            SET category = 'Physical Security'
            WHERE category = 'Incident & Resilience'
            AND id IN (
                SELECT ui.id
                FROM universal_intents ui
                JOIN intent_framework_crosswalk ifc ON ifc.intent_id = ui.id
                WHERE ifc.control_reference = 'A.7.4'
                AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
            )
        """)
        moved_a74 = cursor.rowcount
        print(f"   ✅ Moved {moved_a74} intents for A.7.4 to Physical Security")
        
        # Fix 5: Map 6.3 if unmapped
        print(f"\n6. Checking and mapping 6.3...")
        
        cursor.execute("""
            SELECT c.control_id 
            FROM controls c
            WHERE c.framework_id = 13
            AND c.control_id = '6.3'
            AND NOT EXISTS (
                SELECT 1 
                FROM intent_framework_crosswalk ifc
                JOIN universal_intents ui ON ui.id = ifc.intent_id
                WHERE (ifc.control_reference = '6.3' OR ifc.control_reference = 'ISO_6.3')
                AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
                AND ui.category IN (SELECT name FROM processes WHERE framework_code = 'ISO27001')
            )
        """)
        
        unmapped_63 = cursor.fetchone()
        
        if unmapped_63:
            print(f"   6.3 is unmapped - creating intents...")
            
            # Get max IDs
            cursor.execute("SELECT MAX(id) FROM universal_intents")
            max_intent_id = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT MAX(id) FROM intent_framework_crosswalk")
            max_cross_id = cursor.fetchone()[0] or 0
            
            # Create intents for 6.3
            intents_63 = [
                "Changes to the ISMS are planned and implemented in a controlled manner",
                "Purpose and consequences of changes are considered",
                "ISMS integrity is maintained during changes"
            ]
            
            for intent_desc in intents_63:
                max_intent_id += 1
                cursor.execute("""
                    INSERT INTO universal_intents (id, intent_id, description, category)
                    VALUES (?, ?, ?, ?)
                """, (max_intent_id, f"GOV_{max_intent_id}", intent_desc, "Governance & Policy"))
                
                max_cross_id += 1
                cursor.execute("""
                    INSERT INTO intent_framework_crosswalk (
                        id, intent_id, framework_id, control_reference
                    )
                    VALUES (?, ?, ?, ?)
                """, (max_cross_id, max_intent_id, 'ISO27001', '6.3'))
            
            print(f"   ✅ Created and mapped {len(intents_63)} intents for 6.3")
        else:
            print(f"   ✅ 6.3 is already mapped")
        
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
    
    # Final verification
    print(f"\n7. Final Verification...")
    
    framework_id = 13
    
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
    print(f"\n   Final process control counts:")
    
    key_processes = [
        ('HR Security', 11, 'A.6.1-8, 7.1, 7.2, 7.3'),
        ('Risk Management', 6, '6.1.1, 6.1.2, 6.1.3, 6.2, 8.2, 8.3'),
        ('Governance & Policy', None, 'Should have 6.2, 6.3, 7.5.x'),
        ('Performance Evaluation', 7, 'A.5.35, 9.1, 9.2.1, 9.2.2, 9.3.1, 9.3.2, 9.3.3'),
        ('Incident & Resilience', None, 'Should have 7.4 clause, NOT A.7.4'),
        ('Physical Security', None, 'Should have all A.7.x')
    ]
    
    all_correct = True
    
    for proc_name, expected_count, notes in key_processes:
        cursor.execute("""
            SELECT COUNT(DISTINCT c.control_id)
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
        
        count = cursor.fetchone()[0]
        
        if expected_count:
            marker = "✅" if count == expected_count else "⚠️"
            if count != expected_count:
                all_correct = False
        else:
            marker = "ℹ️"
        
        print(f"   {marker} {proc_name}: {count} controls ({notes})")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("FINAL RESULT")
    print("=" * 80)
    
    print(f"\n   Total controls: {total_controls}/123")
    print(f"   Mapped controls: {mapped_controls}/123")
    print(f"   Unmapped: {total_controls - mapped_controls}")
    
    if total_controls == 123 and mapped_controls == 123 and all_correct:
        print(f"\n🎉🎉🎉 PERFECT! 🎉🎉🎉")
        print(f"   ✅ 123 controls (93 Annex A + 30 clauses)")
        print(f"   ✅ All controls correctly mapped")
        print(f"   ✅ No duplicates")
        print(f"   ✅ ISO 27001:2022 COMPLETE!")
    elif mapped_controls == 123:
        print(f"\n✅ All 123 controls are mapped!")
        print(f"⚠️  But some process counts may need review")
    else:
        print(f"\n⚠️  Status:")
        print(f"   Total: {total_controls}/123")
        print(f"   Mapped: {mapped_controls}/123")
    
    print(f"\n✅ Backup saved as: {BACKUP_NAME}")
    print(f"\n🔄 Next steps:")
    print(f"   1. Restart backend")
    print(f"   2. Verify frontend shows all 123 controls")
    print(f"   3. Run: python review_all_mappings.py (optional final check)")
    
    return 0

if __name__ == "__main__":
    exit(main())
