import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_csv(r"C:\Projects\Compliance_Product\Backend\MASTER_ISO27001_INTENTS.csv")
print(df[['Intent_id', 'Clause_or_control', 'Action_Title']].head(5))
print(f"Total Rows: {len(df)}")
print(f"Unique Intent_ids: {len(df['Intent_id'].unique())}")
print(f"Unique Clauses: {len(df['Clause_or_control'].unique())}")
