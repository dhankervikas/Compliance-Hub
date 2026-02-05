import pandas as pd
import os

ASSET_DIR = r"C:\Users\dhank\OneDrive\Documents\Compliance_Product\Backend\Assets\AI Framework Modules"
files = [f for f in os.listdir(ASSET_DIR) if f.endswith('.xlsx')]

print(f"Found {len(files)} files.")

for f in files:
    path = os.path.join(ASSET_DIR, f)
    try:
        df = pd.read_excel(path, nrows=0)
        print(f"\nFile: {f}")
        print(f"Columns: {list(df.columns)}")
    except Exception as e:
        print(f"Error reading {f}: {e}")
