
import pandas as pd
import os

file_path = "app/static/reports/AI_ISO_42001_Mapping_Report.xlsx"
full_path = os.path.abspath(file_path)

print(f"Checking file: {full_path}")

if not os.path.exists(full_path):
    print("File not found!")
else:
    try:
        df = pd.read_excel(full_path)
        print(f"Total Rows: {len(df)}")
        if "AI Category" in df.columns:
            print("AI Categories Found:")
            print(df["AI Category"].unique())
        else:
            print("Column 'AI Category' not found!")
            print("Columns:", df.columns)
            
    except Exception as e:
        print(f"Error reading file: {e}")
