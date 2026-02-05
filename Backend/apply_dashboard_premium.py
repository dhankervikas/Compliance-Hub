
import os

source_file = "Dashboard_Premium.js"
target_file = r"..\..\Frontend\src\components\Dashboard.js"

try:
    with open(source_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"SUCCESS: Replaced Dashboard.js with Premium Layout.")
except Exception as e:
    print(f"Error: {e}")
