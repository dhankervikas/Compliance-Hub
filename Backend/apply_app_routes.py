
import os

source_file = "App_Premium.js"
target_file = r"..\..\Frontend\src\App.js"

try:
    with open(source_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"SUCCESS: Replaced App.js with Premium Routes.")
except Exception as e:
    print(f"Error: {e}")
