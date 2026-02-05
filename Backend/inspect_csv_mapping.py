import csv
import sys

def inspect_mapping():
    filename = "MASTER_ISO27001_INTENTS.csv"
    try:
        with open(filename, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            print(f"--- INSPECTING {filename} ---")
            print(f"Columns: {reader.fieldnames}")
            
            found_4_1 = 0
            found_A_5_1 = 0
            
            for row in reader:
                id_val = row.get('Clause_or_control', '').strip()
                title = row.get('Action_Title', '').strip()
                intent = row.get('Intent_statement', '').strip()
                
                if id_val == '4.1':
                    found_4_1 += 1
                    if found_4_1 <= 3: # valid sample
                        print(f"\n[ROW for 4.1]")
                        print(f"  ID: {id_val}")
                        print(f"  Title: {title}")
                        print(f"  Intent: {intent}")

                if id_val == 'A.5.1': # Or '5.1'
                    found_A_5_1 += 1
                    if found_A_5_1 <= 3:
                        print(f"\n[ROW for A.5.1]")
                        print(f"  ID: {id_val}")
                        print(f"  Title: {title}")
                        print(f"  Intent: {intent}")
                        
                 # Also check for the specific wrong string the user mentioned
                if "The information security policy is available" in title:
                     print(f"\n[FOUND MISMATCHED TITLE]")
                     print(f"  Attached to ID: {id_val}")
                     print(f"  Title: {title}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_mapping()
