import pandas as pd
import os

files = [
    r"C:\Users\dhank\OneDrive\Documents\Compliance_Product\Backend\iso27001_intent_library.csv",
    r"C:\Users\dhank\OneDrive\Documents\Compliance_Product\Backend\Intents.csv"
]

for f in files:
    print(f"--- Analyzing {os.path.basename(f)} from ONEDRIVE ---")
    if not os.path.exists(f):
        print("File does not exist.")
        continue
        
    try:
        # Try default utf-8 first, then fallbacks
        try:
            df = pd.read_csv(f, encoding='utf-8')
        except UnicodeDecodeError:
            print("UTF-8 failed, trying latin1...")
            df = pd.read_csv(f, encoding='latin1')
            
        print(f"Rows: {len(df)}")
        print("Columns:", list(df.columns))
        
        has_process = "Process" in df.columns
        has_status = "compliance_status" in df.columns
        print(f"Has 'Process' column: {has_process}")
        print(f"Has 'compliance_status' column: {has_status}")
        
    except Exception as e:
        print(f"Error reading {f}: {e}")
