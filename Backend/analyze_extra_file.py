import pandas as pd
import os

files = [
    r"C:\Projects\Compliance_Product\Backend\Intents.csv.xlsx"
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
            df = pd.read_excel(f, sheet_name=sheet, nrows=5)
            cols = list(df.columns)
            print(f"Columns ({len(cols)}): {cols}")
            
    except Exception as e:
        print(f"Error reading {f}: {e}")
