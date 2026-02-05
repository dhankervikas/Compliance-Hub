"""
Merge Internal Audit + Management Review into new "Performance Evaluation" process
Also delete "Operations (General)"
Result: 24 → 22 processes
"""

import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

DB_PATH = "sql_app.db"
BACKUP_NAME = f"backup_create_performance_eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

def main():
    print("=" * 80)
    print("CREATE: Performance Evaluation Process")
    print("MERGE: Internal Audit + Management Review")
    print("DELETE: Operations (General)")
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
    
    # Connect
    print(f"\n2. Connecting to database...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Current count
    print(f"\n3. Checking current state...")
    cursor.execute("SELECT COUNT(*) FROM processes WHERE framework_code='ISO27001'")
    before = cursor.fetchone()[0]
    print(f"   Current ISO27001 processes: {before}")
    
    # Check processes to merge
    cursor.execute("SELECT id, name FROM processes WHERE id IN (51, 52) AND framework_code='ISO27001'")
    to_merge = cursor.fetchall()
    print(f"\n   Processes to merge:")
    for proc_id, name in to_merge:
        cursor.execute("SELECT COUNT(*) FROM universal_intents WHERE category=?", (name,))
        intent_count = cursor.fetchone()[0]
        print(f"      - ID {proc_id}: '{name}' ({intent_count} intents)")
    
    # Check Operations (General)
    cursor.execute("SELECT id, name FROM processes WHERE id=36 AND framework_code='ISO27001'")
    ops_general = cursor.fetchone()
    if ops_general:
        print(f"   Process to delete:")
        print(f"      - ID {ops_general[0]}: '{ops_general[1]}' (0 intents)")
    
    try:
        # Step 1: Create new "Performance Evaluation" process
        print(f"\n4. Creating new process: 'Performance Evaluation'...")
        
        # Get max ID to create new one
        cursor.execute("SELECT MAX(id) FROM processes")
        max_id = cursor.fetchone()[0]
        new_id = max_id + 1
        
        cursor.execute("""
            INSERT INTO processes (id, name, description, framework_code)
            VALUES (?, ?, ?, ?)
        """, (new_id, 
              "Performance Evaluation", 
              "Core Process: Performance Evaluation (Clause 9 - Internal Audit & Management Review)",
              "ISO27001"))
        
        print(f"   ✅ Created: 'Performance Evaluation' (ID {new_id})")
        
        # Step 2: Move intents from Internal Audit to Performance Evaluation
        print(f"\n5. Moving intents from 'Internal Audit' to 'Performance Evaluation'...")
        cursor.execute("""
            UPDATE universal_intents
            SET category = 'Performance Evaluation'
            WHERE category = 'Internal Audit'
        """)
        audit_intents = cursor.rowcount
        print(f"   ✅ Moved {audit_intents} intents from Internal Audit")
        
        # Step 3: Move intents from Management Review to Performance Evaluation
        print(f"\n6. Moving intents from 'Management Review' to 'Performance Evaluation'...")
        cursor.execute("""
            UPDATE universal_intents
            SET category = 'Performance Evaluation'
            WHERE category = 'Management Review'
        """)
        review_intents = cursor.rowcount
        print(f"   ✅ Moved {review_intents} intents from Management Review")
        
        total_intents = audit_intents + review_intents
        print(f"\n   📊 Performance Evaluation now has: {total_intents} intents")
        
        # Step 4: Delete old processes
        print(f"\n7. Deleting old processes...")
        
        # Delete Internal Audit
        cursor.execute("DELETE FROM processes WHERE id=51 AND framework_code='ISO27001'")
        print(f"   ✅ Deleted: 'Internal Audit' (ID 51)")
        
        # Delete Management Review
        cursor.execute("DELETE FROM processes WHERE id=52 AND framework_code='ISO27001'")
        print(f"   ✅ Deleted: 'Management Review' (ID 52)")
        
        # Delete Operations (General)
        cursor.execute("DELETE FROM processes WHERE id=36 AND framework_code='ISO27001'")
        print(f"   ✅ Deleted: 'Operations (General)' (ID 36)")
        
        # Commit changes
        conn.commit()
        print(f"\n   ✅ All changes committed to database")
        
    except Exception as e:
        print(f"\n   ❌ Error: {e}")
        conn.rollback()
        print(f"   ⚠️  Changes rolled back")
        conn.close()
        return 1
    
    # Verify final state
    print(f"\n8. Verifying results...")
    cursor.execute("SELECT COUNT(*) FROM processes WHERE framework_code='ISO27001'")
    after = cursor.fetchone()[0]
    
    print(f"\n   Before: {before} processes")
    print(f"   Deleted: 3 processes (Internal Audit, Management Review, Operations General)")
    print(f"   Created: 1 process (Performance Evaluation)")
    print(f"   After: {after} processes")
    
    if after == 22:
        print(f"\n   🎉 SUCCESS! Reached target of 22 processes!")
    else:
        print(f"\n   ⚠️  Expected 22, got {after}")
    
    # List all processes
    print(f"\n9. All ISO27001 processes:")
    cursor.execute("""
        SELECT p.id, p.name, COUNT(ui.id) as intent_count
        FROM processes p
        LEFT JOIN universal_intents ui ON ui.category = p.name
        WHERE p.framework_code = 'ISO27001'
        GROUP BY p.id, p.name
        ORDER BY p.name
    """)
    
    processes = cursor.fetchall()
    for proc_id, name, intent_count in processes:
        marker = "✅" if intent_count > 0 else "⚠️"
        print(f"   {marker} {proc_id:3}. {name:<45} ({intent_count} intents)")
    
    # Verify Performance Evaluation
    print(f"\n10. Verifying Performance Evaluation controls...")
    cursor.execute("""
        SELECT DISTINCT c.control_id, c.title
        FROM controls c
        JOIN intent_framework_crosswalk ifc ON (
            ifc.control_reference = c.control_id OR
            ifc.control_reference = 'ISO_' || c.control_id
        )
        JOIN universal_intents ui ON ui.id = ifc.intent_id
        WHERE c.framework_id = 13
        AND ui.category = 'Performance Evaluation'
        AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
        ORDER BY c.control_id
    """)
    
    perf_controls = cursor.fetchall()
    print(f"\n    Performance Evaluation has {len(perf_controls)} controls:")
    for ctrl_id, title in perf_controls:
        print(f"       ✅ {ctrl_id}: {title[:55]}")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("RESTRUCTURING COMPLETE")
    print("=" * 80)
    print(f"\n✅ Backup saved as: {BACKUP_NAME}")
    print(f"✅ Created: 'Performance Evaluation' (merged Internal Audit + Management Review)")
    print(f"✅ Deleted: 'Operations (General)' (had 0 intents)")
    print(f"✅ Final count: {after} processes (Target: 22) {'✅' if after == 22 else '❌'}")
    print(f"\n🔄 Next steps:")
    print(f"   1. Restart backend to apply changes")
    print(f"   2. Check frontend - should see:")
    print(f"      - 'Performance Evaluation' process (new)")
    print(f"      - No more 'Internal Audit' or 'Management Review'")
    print(f"      - Total: 22 processes")
    print(f"   3. Then run: python step2_fix_mappings.py")
    
    return 0

if __name__ == "__main__":
    exit(main())
