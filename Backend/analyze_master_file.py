import pandas as pd
import os

files = [
    r"C:\Projects\Compliance_Product\Controls\Intent Framework.xlsx",
    r"C:\Projects\Compliance_Product\Controls\iso27001_product_logic.xlsx"
]

for f in files:
    print(f"\n{'='*40}")
    print(f"Analyzing XLSX: {os.path.basename(f)}")
    print(f"{'='*40}")
    
    if not os.path.exists(f):
        print("File does not exist.")
        continue
        
    try:
        xl = pd.ExcelFile(f)
        print("Sheet Names:", xl.sheet_names)
        
        for sheet in xl.sheet_names:
            print(f"\n--- Sheet: {sheet} ---")
            df = pd.read_excel(f, sheet_name=sheet, nrows=5) # Only read headers + 5 rows
            cols = list(df.columns)
            print(f"Columns ({len(cols)}): {cols}")
            
            has_process = "Process" in cols
            has_status = "compliance_status" in cols
            has_intent_id = "Intent_ID" in cols or "Intent ID" in cols
            
            print(f"  [?] Has 'Process': {has_process}")
            print(f"  [?] Has 'compliance_status': {has_status}")
            print(f"  [?] Has 'Intent_ID': {has_intent_id}")
            
    except Exception as e:
        print(f"Error reading {f}: {e}")
