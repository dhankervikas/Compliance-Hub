"""
Analyze which 2 more processes should be deleted (24 → 22)
Shows intent counts to help decide
"""

import sqlite3

DB_PATH = "sql_app.db"

def main():
    print("=" * 80)
    print("ANALYSIS: Which 2 More Processes to Delete?")
    print("=" * 80)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all processes with intent counts
    cursor.execute("""
        SELECT p.id, p.name, COUNT(ui.id) as intent_count
        FROM processes p
        LEFT JOIN universal_intents ui ON ui.category = p.name
        WHERE p.framework_code = 'ISO27001'
        GROUP BY p.id, p.name
        ORDER BY intent_count ASC, p.name
    """)
    
    processes = cursor.fetchall()
    
    print(f"\nCurrent: {len(processes)} processes (Target: 22)")
    print(f"Need to delete: {len(processes) - 22} more processes\n")
    
    print("Processes sorted by intent count (lowest first):")
    print("-" * 80)
    print(f"{'ID':<5} {'Intent Count':<13} {'Process Name':<50}")
    print("-" * 80)
    
    candidates_for_deletion = []
    
    for proc_id, name, intent_count in processes:
        marker = ""
        if intent_count == 0:
            marker = "⚠️ EMPTY - DELETE THIS"
            candidates_for_deletion.append((proc_id, name, intent_count, "Has 0 intents"))
        elif intent_count < 7:
            marker = "⚠️ Very few intents"
        
        print(f"{proc_id:<5} {intent_count:<13} {name:<50} {marker}")
    
    # Check for potential name duplicates
    print("\n" + "=" * 80)
    print("CHECKING FOR SIMILAR/DUPLICATE NAMES:")
    print("=" * 80)
    
    names = [(p[0], p[1]) for p in processes]
    found_similar = False
    
    for i, (id1, name1) in enumerate(names):
        for id2, name2 in names[i+1:]:
            # Check if names are similar
            n1_lower = name1.lower().replace('(', '').replace(')', '')
            n2_lower = name2.lower().replace('(', '').replace(')', '')
            
            # Check if one is substring of other or they share major words
            if ('operations' in n1_lower and 'operations' in n2_lower) or \
               (n1_lower in n2_lower or n2_lower in n1_lower):
                print(f"\n⚠️ Potential duplicate:")
                print(f"   ID {id1}: '{name1}'")
                print(f"   ID {id2}: '{name2}'")
                
                # Get intent counts for these
                cursor.execute("SELECT COUNT(*) FROM universal_intents WHERE category=?", (name1,))
                count1 = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM universal_intents WHERE category=?", (name2,))
                count2 = cursor.fetchone()[0]
                
                print(f"   {name1}: {count1} intents")
                print(f"   {name2}: {count2} intents")
                
                if count1 > count2:
                    print(f"   → Recommend: DELETE '{name2}' (ID {id2})")
                    candidates_for_deletion.append((id2, name2, count2, f"Duplicate of '{name1}'"))
                else:
                    print(f"   → Recommend: DELETE '{name1}' (ID {id1})")
                    candidates_for_deletion.append((id1, name1, count1, f"Duplicate of '{name2}'"))
                
                found_similar = True
    
    if not found_similar:
        print("\n✅ No obvious name duplicates found")
    
    # Recommendations
    print("\n" + "=" * 80)
    print("RECOMMENDED DELETIONS:")
    print("=" * 80)
    
    if candidates_for_deletion:
        # Remove duplicates and sort by intent count
        unique_candidates = list(set(candidates_for_deletion))
        unique_candidates.sort(key=lambda x: x[2])  # Sort by intent count
        
        print(f"\nTop candidates to delete (need to pick 2):\n")
        for i, (proc_id, name, intent_count, reason) in enumerate(unique_candidates[:5], 1):
            print(f"{i}. ID {proc_id}: '{name}' ({intent_count} intents)")
            print(f"   Reason: {reason}\n")
        
        if len(unique_candidates) >= 2:
            print("=" * 80)
            print("AUTOMATIC RECOMMENDATION:")
            print("=" * 80)
            top_two = unique_candidates[:2]
            print(f"\nDelete these 2 processes:")
            for proc_id, name, intent_count, reason in top_two:
                print(f"   ❌ ID {proc_id}: '{name}' - {reason}")
            
            print(f"\nThis will reduce from {len(processes)} to {len(processes) - 2} processes (target: 22)")
    else:
        print("\n⚠️ No clear candidates identified")
        print("Manual review needed to choose which 2 to merge/delete")
    
    conn.close()
    
    return 0

if __name__ == "__main__":
    exit(main())
