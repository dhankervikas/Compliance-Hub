
import os

source_file = "FrameworkDetail_SOC2.js"
target_file = r"..\..\Frontend\src\components\FrameworkDetail.js"

try:
    with open(source_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"SUCCESS: Replaced FrameworkDetail.js with SOC 2 Specialized View.")
except Exception as e:
    print(f"Error: {e}")
