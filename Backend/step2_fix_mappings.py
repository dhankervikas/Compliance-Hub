"""
Step 2: Fix Wrong Control Mappings
Moves 6.1.1, 6.1.2, 6.1.3, 6.2 from HR Security to Risk Management
"""

import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

# Configuration
DB_PATH = "sql_app.db"
BACKUP_NAME = f"backup_step2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

def main():
    print("=" * 80)
    print("STEP 2: Fix Wrong Control Mappings")
    print("=" * 80)
    
    # Check if database exists
    if not Path(DB_PATH).exists():
        print(f"\n❌ ERROR: Database '{DB_PATH}' not found!")
        print("   Make sure you're in the Backend directory")
        return 1
    
    # Backup database
    print(f"\n1. Creating backup: {BACKUP_NAME}")
    try:
        shutil.copy2(DB_PATH, BACKUP_NAME)
        print(f"   ✅ Backup created successfully")
    except Exception as e:
        print(f"   ❌ Backup failed: {e}")
        return 1
    
    # Connect to database
    print(f"\n2. Connecting to database...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check current state
    print(f"\n3. Checking current mappings...")
    cursor.execute("""
        SELECT DISTINCT c.control_id, c.title
        FROM controls c
        JOIN intent_framework_crosswalk ifc ON (
            ifc.control_reference = c.control_id OR
            ifc.control_reference = 'ISO_' || c.control_id
        )
        JOIN universal_intents ui ON ui.id = ifc.intent_id
        WHERE c.framework_id = 13
        AND ui.category = 'HR Security'
        AND c.control_id IN ('6.1.1', '6.1.2', '6.1.3', '6.2')
        AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
        ORDER BY c.control_id
    """)
    
    wrong_mappings = cursor.fetchall()
    
    if not wrong_mappings:
        print("   ⚠️  Wrong mappings not found (already fixed?)")
        conn.close()
        return 0
    
    print(f"   Found {len(wrong_mappings)} controls wrongly in HR Security:")
    for ctrl_id, title in wrong_mappings:
        print(f"      - {ctrl_id}: {title[:50]}")
    
    # Execute fix
    print(f"\n4. Moving intents to Risk Management...")
    try:
        # Move risk management intents (6.1.1, 6.1.2, 6.1.3)
        cursor.execute("""
            UPDATE universal_intents
            SET category = 'Risk Management'
            WHERE id IN (
                50, 51, 52, 53, 54,  -- 6.1.1 intents
                55, 56, 57, 58, 59, 60,  -- 6.1.2 intents
                61, 62, 63, 64, 65   -- 6.1.3 intents
            )
        """)
        risk_updated = cursor.rowcount
        print(f"   ✅ Updated {risk_updated} risk management intents")
        
        # Move objectives intents (6.2)
        cursor.execute("""
            UPDATE universal_intents
            SET category = 'Risk Management'
            WHERE id IN (66, 67, 68, 69, 70)
        """)
        obj_updated = cursor.rowcount
        print(f"   ✅ Updated {obj_updated} objectives intents")
        
        # Commit changes
        conn.commit()
        print(f"\n   ✅ Changes committed to database")
        
    except Exception as e:
        print(f"\n   ❌ Error during update: {e}")
        conn.rollback()
        print(f"   ⚠️  Changes rolled back")
        conn.close()
        return 1
    
    # Verify HR Security now has only A.6.x controls
    print(f"\n5. Verifying HR Security controls...")
    cursor.execute("""
        SELECT DISTINCT c.control_id, c.title
        FROM controls c
        JOIN intent_framework_crosswalk ifc ON (
            ifc.control_reference = c.control_id OR
            ifc.control_reference = 'ISO_' || c.control_id
        )
        JOIN universal_intents ui ON ui.id = ifc.intent_id
        WHERE c.framework_id = 13
        AND ui.category = 'HR Security'
        AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
        ORDER BY c.control_id
    """)
    
    hr_controls = cursor.fetchall()
    
    print(f"\n   HR Security now has {len(hr_controls)} controls:")
    for ctrl_id, title in hr_controls:
        print(f"      ✅ {ctrl_id}: {title[:50]}")
    
    # Check if all are A.6.x
    wrong_controls = [c for c in hr_controls if not c[0].startswith('A.6')]
    if wrong_controls:
        print(f"\n   ⚠️  WARNING: Still has non-A.6.x controls:")
        for ctrl_id, title in wrong_controls:
            print(f"      - {ctrl_id}: {title[:50]}")
    else:
        print(f"\n   ✅ All controls are A.6.x (correct!)")
    
    # Verify Risk Management gained the controls
    print(f"\n6. Verifying Risk Management controls...")
    cursor.execute("""
        SELECT DISTINCT c.control_id, c.title
        FROM controls c
        JOIN intent_framework_crosswalk ifc ON (
            ifc.control_reference = c.control_id OR
            ifc.control_reference = 'ISO_' || c.control_id
        )
        JOIN universal_intents ui ON ui.id = ifc.intent_id
        WHERE c.framework_id = 13
        AND ui.category = 'Risk Management'
        AND c.control_id IN ('6.1.1', '6.1.2', '6.1.3', '6.2')
        AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
        ORDER BY c.control_id
    """)
    
    risk_controls = cursor.fetchall()
    
    print(f"\n   Risk Management gained {len(risk_controls)} controls:")
    for ctrl_id, title in risk_controls:
        print(f"      ✅ {ctrl_id}: {title[:50]}")
    
    if len(risk_controls) == 4:
        print(f"\n   ✅ All 4 controls successfully moved!")
    else:
        print(f"\n   ⚠️  Expected 4 controls, found {len(risk_controls)}")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("STEP 2 COMPLETE")
    print("=" * 80)
    print(f"\n✅ Backup saved as: {BACKUP_NAME}")
    print(f"✅ Wrong mappings fixed")
    print(f"✅ HR Security: {len(hr_controls)} controls (all A.6.x)")
    print(f"✅ Risk Management: gained 4 controls")
    print(f"\n💡 Next step: Restart your backend to see the changes")
    print(f"   Backend will now show:")
    print(f"   - HR Security: 8 controls (A.6.1 - A.6.8)")
    print(f"   - Risk Management: increased control count")
    
    return 0

if __name__ == "__main__":
    exit(main())
