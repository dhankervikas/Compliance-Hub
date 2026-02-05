import csv
import os

def analyze():
    csv_path = "Backend/MASTER_ISO27001_INTENTS.csv"
    unique_titles = {}
    
    encodings = ['utf-8', 'cp1252', 'latin1']
    rows = []
    
    for enc in encodings:
        try:
            with open(csv_path, mode='r', encoding=enc) as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            break
        except UnicodeDecodeError: continue
        except FileNotFoundError:
            print(f"File not found: {csv_path}")
            return

    for row in rows:
        clause = row.get('Clause_or_control')
        # Ensure A. prefix for 5-8
        if clause and clause[0].isdigit() and clause.startswith(('5','6','7','8')):
             clause = f"A.{clause}"
             
        title = row.get('Action_Title', '').strip()
        standard = row.get('Standard')
        
        # Only care about Annex A controls likely
        if clause not in unique_titles:
            unique_titles[clause] = title
        else:
            # Check consistency?
            pass

    # Print relevant Annex A controls
    print(f"{'Clause':<10} | {'Current Action Title'}")
    print("-" * 80)
    for clause, title in unique_titles.items():
        if clause.startswith('A.'):
            try:
                print(f"{clause:<10} | {title}")
            except UnicodeEncodeError:
                print(f"{clause:<10} | {title.encode('ascii', errors='replace').decode('ascii')}")

if __name__ == "__main__":
    analyze()
