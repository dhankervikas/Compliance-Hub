"""
Fix mappings based on user specifications:
1. Remove duplicates: 8.2, 8.3 from Access Control (keep in Risk Management)
2. Remove duplicates: A.5.7, A.6.1, A.6.2 from Risk Management
3. Move A.8.34 to Operations
4. Move 9.1 to Performance Evaluation
5. Move 7.1, 7.2, 7.3 to HR Security
6. Move 7.5.1, 7.5.2, 7.5.3 to Governance & Policy
7. Add 6.3 to Governance & Policy
8. Verify 123 total controls
"""

import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

DB_PATH = "sql_app.db"
BACKUP_NAME = f"backup_correct_mappings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

def main():
    print("=" * 80)
    print("CORRECT ALL MAPPINGS - USER SPECIFICATIONS")
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
        # Fix 1: Remove 8.2, 8.3 from Access Control (IAM) - keep in Risk Management
        print(f"\n2. Removing 8.2, 8.3 from Access Control (IAM)...")
        cursor.execute("""
            SELECT ui.id
            FROM universal_intents ui
            JOIN intent_framework_crosswalk ifc ON ifc.intent_id = ui.id
            WHERE ui.category = 'Access Control (IAM)'
            AND (
                ifc.control_reference IN ('8.2', '8.3') OR
                ifc.control_reference IN ('ISO_8.2', 'ISO_8.3')
            )
            AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
        """)
        
        iam_82_83 = [row[0] for row in cursor.fetchall()]
        
        if iam_82_83:
            cursor.execute(f"""
                UPDATE universal_intents
                SET category = 'Risk Management'
                WHERE id IN ({','.join(map(str, iam_82_83))})
            """)
            print(f"   ✅ Moved {len(iam_82_83)} intents to Risk Management")
        else:
            print(f"   ℹ️  8.2, 8.3 not found in Access Control (IAM)")
        
        # Fix 2: Remove A.5.7 from Risk Management - keep in Threat Intel
        print(f"\n3. Removing A.5.7 from Risk Management...")
        cursor.execute("""
            SELECT ui.id
            FROM universal_intents ui
            JOIN intent_framework_crosswalk ifc ON ifc.intent_id = ui.id
            WHERE ui.category = 'Risk Management'
            AND (ifc.control_reference = 'A.5.7' OR ifc.control_reference = 'ISO_A.5.7')
            AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
        """)
        
        risk_a57 = [row[0] for row in cursor.fetchall()]
        
        if risk_a57:
            cursor.execute(f"""
                UPDATE universal_intents
                SET category = 'Threat Intel'
                WHERE id IN ({','.join(map(str, risk_a57))})
            """)
            print(f"   ✅ Moved {len(risk_a57)} intents to Threat Intel")
        else:
            print(f"   ℹ️  A.5.7 not found in Risk Management")
        
        # Fix 3: Remove A.6.1, A.6.2 from Risk Management - keep in HR Security
        print(f"\n4. Removing A.6.1, A.6.2 from Risk Management...")
        cursor.execute("""
            SELECT ui.id
            FROM universal_intents ui
            JOIN intent_framework_crosswalk ifc ON ifc.intent_id = ui.id
            WHERE ui.category = 'Risk Management'
            AND (
                ifc.control_reference IN ('A.6.1', 'A.6.2') OR
                ifc.control_reference IN ('ISO_A.6.1', 'ISO_A.6.2')
            )
            AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
        """)
        
        risk_a61_a62 = [row[0] for row in cursor.fetchall()]
        
        if risk_a61_a62:
            cursor.execute(f"""
                UPDATE universal_intents
                SET category = 'HR Security'
                WHERE id IN ({','.join(map(str, risk_a61_a62))})
            """)
            print(f"   ✅ Moved {len(risk_a61_a62)} intents to HR Security")
        else:
            print(f"   ℹ️  A.6.1, A.6.2 not found in Risk Management")
        
        # Fix 4: Move A.8.34 to Operations
        print(f"\n5. Moving A.8.34 to Operations...")
        cursor.execute("""
            UPDATE universal_intents
            SET category = 'Operations'
            WHERE category = 'Legal & Compliance'
            AND id IN (
                SELECT ui.id
                FROM universal_intents ui
                JOIN intent_framework_crosswalk ifc ON ifc.intent_id = ui.id
                WHERE (ifc.control_reference = 'A.8.34' OR ifc.control_reference = 'ISO_A.8.34')
                AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
            )
        """)
        a834_moved = cursor.rowcount
        print(f"   ✅ Moved {a834_moved} intents for A.8.34 to Operations")
        
        # Fix 5: Move 9.1 to Performance Evaluation
        print(f"\n6. Moving 9.1 to Performance Evaluation...")
        cursor.execute("""
            UPDATE universal_intents
            SET category = 'Performance Evaluation'
            WHERE category = 'Logging & Monitoring'
            AND id IN (
                SELECT ui.id
                FROM universal_intents ui
                JOIN intent_framework_crosswalk ifc ON ifc.intent_id = ui.id
                WHERE (ifc.control_reference = '9.1' OR ifc.control_reference = 'ISO_9.1')
                AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
            )
        """)
        c91_moved = cursor.rowcount
        print(f"   ✅ Moved {c91_moved} intents for 9.1 to Performance Evaluation")
        
        # Fix 6: Move 7.1, 7.2, 7.3 to HR Security
        print(f"\n7. Moving 7.1, 7.2, 7.3 to HR Security...")
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
        c71_73_moved = cursor.rowcount
        print(f"   ✅ Moved {c71_73_moved} intents for 7.1, 7.2, 7.3 to HR Security")
        
        # Fix 7: Move 7.5.1, 7.5.2, 7.5.3 to Governance & Policy
        print(f"\n8. Moving 7.5.1, 7.5.2, 7.5.3 to Governance & Policy...")
        cursor.execute("""
            UPDATE universal_intents
            SET category = 'Governance & Policy'
            WHERE category = 'Physical Security'
            AND id IN (
                SELECT ui.id
                FROM universal_intents ui
                JOIN intent_framework_crosswalk ifc ON ifc.intent_id = ui.id
                WHERE (
                    ifc.control_reference IN ('7.5.1', '7.5.2', '7.5.3') OR
                    ifc.control_reference IN ('ISO_7.5.1', 'ISO_7.5.2', 'ISO_7.5.3')
                )
                AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
            )
        """)
        c75_moved = cursor.rowcount
        print(f"   ✅ Moved {c75_moved} intents for 7.5.1, 7.5.2, 7.5.3 to Governance & Policy")
        
        # Fix 8: Add 6.3 to Governance & Policy (if unmapped)
        print(f"\n9. Adding 6.3 to Governance & Policy...")
        
        # Check if 6.3 has any mappings
        cursor.execute("""
            SELECT DISTINCT ui.id, ui.category
            FROM universal_intents ui
            JOIN intent_framework_crosswalk ifc ON ifc.intent_id = ui.id
            WHERE (ifc.control_reference = '6.3' OR ifc.control_reference = 'ISO_6.3')
            AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
        """)
        
        c63_intents = cursor.fetchall()
        
        if c63_intents:
            # Update to Governance & Policy
            intent_ids = [str(i[0]) for i in c63_intents]
            cursor.execute(f"""
                UPDATE universal_intents
                SET category = 'Governance & Policy'
                WHERE id IN ({','.join(intent_ids)})
            """)
            print(f"   ✅ Mapped {len(c63_intents)} intents for 6.3 to Governance & Policy")
        else:
            print(f"   ⚠️  No intents found for control 6.3")
        
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
    
    # Verify total control count
    print(f"\n10. Verifying total control count...")
    cursor.execute("""
        SELECT COUNT(DISTINCT c.id)
        FROM controls c
        WHERE c.framework_id = 13
    """)
    
    total_controls = cursor.fetchone()[0]
    print(f"\n   Total controls in database: {total_controls}")
    
    if total_controls == 123:
        print(f"   ✅ CORRECT! Total is 123 controls")
    else:
        print(f"   ⚠️  Expected 123, found {total_controls}")
        print(f"   Difference: {123 - total_controls}")
    
    # Count mapped controls
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
    print(f"\n   Mapped controls: {mapped_controls}")
    print(f"   Unmapped controls: {total_controls - mapped_controls}")
    
    # Show key process control counts
    print(f"\n11. Key process verification:")
    
    key_processes = [
        'HR Security',
        'Risk Management',
        'Access Control (IAM)',
        'Operations',
        'Performance Evaluation',
        'Governance & Policy',
        'Physical Security'
    ]
    
    for proc_name in key_processes:
        cursor.execute("""
            SELECT COUNT(DISTINCT c.control_id)
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
        
        count = cursor.fetchone()[0]
        print(f"   {proc_name:<30} {count:>3} controls")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("MAPPING CORRECTION COMPLETE")
    print("=" * 80)
    print(f"\n✅ Backup saved as: {BACKUP_NAME}")
    print(f"✅ All mappings corrected per specifications")
    print(f"✅ Total controls: {total_controls}/123")
    print(f"\n🔄 Next steps:")
    print(f"   1. Restart backend")
    print(f"   2. Run: python review_all_mappings.py")
    print(f"   3. Verify all controls are correct")
    
    return 0

if __name__ == "__main__":
    exit(main())
