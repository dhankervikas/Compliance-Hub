"""
Identify which controls are missing from the database
Compare against ISO 27001:2022 standard (93 Annex A + 30 Clauses = 123)
"""

import sqlite3

DB_PATH = "sql_app.db"

# ISO 27001:2022 Complete Control List
ISO_27001_CLAUSES = [
    '4.1', '4.2', '4.3', '4.4',
    '5.1', '5.2', '5.3',
    '6.1.1', '6.1.2', '6.1.3', '6.2', '6.3',
    '7.1', '7.2', '7.3', '7.4', '7.5.1', '7.5.2', '7.5.3',
    '8.1', '8.2', '8.3',
    '9.1', '9.2', '9.3',
    '10.1', '10.2'
]  # 27 clauses (27001:2022 has 27, not 30)

ISO_27001_ANNEX_A = [
    # A.5: Organizational controls (37)
    'A.5.1', 'A.5.2', 'A.5.3', 'A.5.4', 'A.5.5', 'A.5.6', 'A.5.7', 'A.5.8', 'A.5.9', 'A.5.10',
    'A.5.11', 'A.5.12', 'A.5.13', 'A.5.14', 'A.5.15', 'A.5.16', 'A.5.17', 'A.5.18', 'A.5.19', 'A.5.20',
    'A.5.21', 'A.5.22', 'A.5.23', 'A.5.24', 'A.5.25', 'A.5.26', 'A.5.27', 'A.5.28', 'A.5.29', 'A.5.30',
    'A.5.31', 'A.5.32', 'A.5.33', 'A.5.34', 'A.5.35', 'A.5.36', 'A.5.37',
    # A.6: People controls (8)
    'A.6.1', 'A.6.2', 'A.6.3', 'A.6.4', 'A.6.5', 'A.6.6', 'A.6.7', 'A.6.8',
    # A.7: Physical controls (14)
    'A.7.1', 'A.7.2', 'A.7.3', 'A.7.4', 'A.7.5', 'A.7.6', 'A.7.7', 'A.7.8', 'A.7.9', 'A.7.10',
    'A.7.11', 'A.7.12', 'A.7.13', 'A.7.14',
    # A.8: Technological controls (34)
    'A.8.1', 'A.8.2', 'A.8.3', 'A.8.4', 'A.8.5', 'A.8.6', 'A.8.7', 'A.8.8', 'A.8.9', 'A.8.10',
    'A.8.11', 'A.8.12', 'A.8.13', 'A.8.14', 'A.8.15', 'A.8.16', 'A.8.17', 'A.8.18', 'A.8.19', 'A.8.20',
    'A.8.21', 'A.8.22', 'A.8.23', 'A.8.24', 'A.8.25', 'A.8.26', 'A.8.27', 'A.8.28', 'A.8.29', 'A.8.30',
    'A.8.31', 'A.8.32', 'A.8.33', 'A.8.34'
]  # 93 Annex A controls

ALL_CONTROLS = ISO_27001_CLAUSES + ISO_27001_ANNEX_A  # Should be 120 total (27 + 93)

def main():
    print("=" * 80)
    print("IDENTIFY MISSING CONTROLS")
    print("=" * 80)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all controls in database
    cursor.execute("""
        SELECT control_id 
        FROM controls 
        WHERE framework_id = 13
        ORDER BY control_id
    """)
    
    db_controls = [row[0] for row in cursor.fetchall()]
    
    print(f"\nISO 27001:2022 Standard:")
    print(f"  Clauses: {len(ISO_27001_CLAUSES)}")
    print(f"  Annex A: {len(ISO_27001_ANNEX_A)}")
    print(f"  Total: {len(ALL_CONTROLS)}")
    
    print(f"\nDatabase:")
    print(f"  Total controls: {len(db_controls)}")
    
    # Find missing controls
    missing = []
    for ctrl in ALL_CONTROLS:
        if ctrl not in db_controls:
            missing.append(ctrl)
    
    print(f"\n" + "=" * 80)
    print(f"MISSING CONTROLS: {len(missing)}")
    print("=" * 80)
    
    if missing:
        print(f"\nThese controls are in ISO 27001:2022 but NOT in your database:\n")
        
        # Group by type
        missing_clauses = [c for c in missing if not c.startswith('A.')]
        missing_annex = [c for c in missing if c.startswith('A.')]
        
        if missing_clauses:
            print(f"Missing Clauses ({len(missing_clauses)}):")
            for ctrl in missing_clauses:
                print(f"   ❌ {ctrl}")
        
        if missing_annex:
            print(f"\nMissing Annex A ({len(missing_annex)}):")
            for ctrl in missing_annex:
                print(f"   ❌ {ctrl}")
    else:
        print(f"\n✅ All ISO 27001:2022 controls are in the database!")
    
    # Find extra controls (in DB but not in standard)
    extra = []
    for ctrl in db_controls:
        if ctrl not in ALL_CONTROLS:
            extra.append(ctrl)
    
    if extra:
        print(f"\n" + "=" * 80)
        print(f"EXTRA CONTROLS: {len(extra)}")
        print("=" * 80)
        print(f"\nThese controls are in your database but NOT in ISO 27001:2022:\n")
        for ctrl in extra:
            print(f"   ⚠️  {ctrl}")
    
    # Check unmapped controls
    print(f"\n" + "=" * 80)
    print(f"UNMAPPED CONTROLS")
    print("=" * 80)
    
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
        print(f"\nFound {len(unmapped)} unmapped controls (exist in DB but not mapped to any process):\n")
        for ctrl_id, title in unmapped:
            print(f"   ⚠️  {ctrl_id}: {title}")
    else:
        print(f"\n✅ All controls in database are mapped to processes")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\nISO 27001:2022 Standard: {len(ALL_CONTROLS)} controls")
    print(f"Your Database: {len(db_controls)} controls")
    print(f"Missing: {len(missing)} controls")
    print(f"Extra: {len(extra)} controls")
    print(f"Unmapped: {len(unmapped)} controls")
    
    if len(missing) > 0:
        print(f"\n💡 Next steps:")
        print(f"   1. Review missing controls above")
        print(f"   2. Add them to the database")
        print(f"   3. Map them to appropriate processes")
    
    return 0

if __name__ == "__main__":
    exit(main())
