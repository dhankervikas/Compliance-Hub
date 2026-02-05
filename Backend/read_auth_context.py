
import os

fpath = r"..\..\Frontend\src\contexts\AuthContext.js"

try:
    print(f"\n--- FILE: {os.path.basename(fpath)} ---")
    with open(fpath, "r", encoding="utf-8") as f:
        print(f.read())
except Exception as e:
    print(f"Error reading {fpath}: {e}")
