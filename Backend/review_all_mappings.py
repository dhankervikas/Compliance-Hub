"""
Review ALL control mappings for ALL processes
Shows which controls are mapped to which processes
"""

import sqlite3

DB_PATH = "sql_app.db"

def main():
    print("=" * 100)
    print("COMPREHENSIVE MAPPING REVIEW - ISO27001")
    print("=" * 100)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all processes
    cursor.execute("""
        SELECT id, name 
        FROM processes 
        WHERE framework_code = 'ISO27001'
        ORDER BY name
    """)
    
    processes = cursor.fetchall()
    
    print(f"\nTotal Processes: {len(processes)}\n")
    
    total_mappings = 0
    
    for proc_id, proc_name in processes:
        # Get controls for this process
        cursor.execute("""
            SELECT DISTINCT c.control_id, c.title
            FROM controls c
            JOIN intent_framework_crosswalk ifc ON (
                ifc.control_reference = c.control_id OR
                ifc.control_reference = 'ISO_' || c.control_id
            )
            JOIN universal_intents ui ON ui.id = ifc.intent_id
            WHERE c.framework_id = 13
            AND ui.category = ?
            AND ifc.framework_id IN ('ISO27001', 'ISO_27001')
            ORDER BY c.control_id
        """, (proc_name,))
        
        controls = cursor.fetchall()
        
        if controls:
            print("=" * 100)
            print(f"PROCESS: {proc_name} ({len(controls)} controls)")
            print("=" * 100)
            
            for ctrl_id, title in controls:
                # Determine if it looks correct
                marker = "✅"
                note = ""
                
                # Check for obvious mismatches
                if proc_name == "HR Security" and not ctrl_id.startswith("A.6"):
                    marker = "❌"
                    note = "← WRONG (should be A.6.x only)"
                elif proc_name == "Risk Management" and not (ctrl_id.startswith("6.1") or ctrl_id == "6.2"):
                    marker = "⚠️"
                    note = "← Check if correct"
                elif proc_name == "Physical Security" and not (ctrl_id.startswith("A.7") or ctrl_id.startswith("7.")):
                    marker = "⚠️"
                    note = "← Check if correct"
                elif proc_name == "Access Control (IAM)" and not (ctrl_id.startswith("A.5") or ctrl_id.startswith("A.8") or ctrl_id.startswith("5.") or ctrl_id.startswith("8.")):
                    marker = "⚠️"
                    note = "← Check if correct"
                
                print(f"  {marker} {ctrl_id:<10} {title[:70]:<70} {note}")
            
            print()
            total_mappings += len(controls)
    
    print("=" * 100)
    print(f"SUMMARY")
    print("=" * 100)
    print(f"\nTotal processes: {len(processes)}")
    print(f"Total control mappings: {total_mappings}")
    print(f"\nLegend:")
    print(f"  ✅ = Looks correct")
    print(f"  ❌ = Definitely wrong")
    print(f"  ⚠️  = Needs review")
    
    # Check for unmapped controls
    print("\n" + "=" * 100)
    print("CHECKING FOR UNMAPPED CONTROLS")
    print("=" * 100)
    
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
    
    if unmapped:
        print(f"\n⚠️  Found {len(unmapped)} unmapped controls:\n")
        for ctrl_id, title in unmapped:
            print(f"  {ctrl_id:<10} {title}")
    else:
        print(f"\n✅ All controls are mapped to processes")
    
    conn.close()
    
    print("\n" + "=" * 100)
    print("\n💡 Review the output above and identify:")
    print("   1. Controls marked with ❌ (definitely wrong)")
    print("   2. Controls marked with ⚠️ (need review)")
    print("   3. Any controls that look wrong but are marked ✅")
    print("\n📝 Then provide the corrections and I'll create a fix script")
    
    return 0

if __name__ == "__main__":
    exit(main())
