
import pandas as pd
import os

file_path = "data/AI_Management_Module.xlsx"
sheet_name = "Scoring Matrix"

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    exit(1)

try:
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    print("Columns found:")
    for col in df.columns:
        print(f" - {col}")
    
    print("\nFirst row sample:")
    print(df.iloc[0].to_dict())
    
except Exception as e:
    print(f"Error reading excel: {e}")
