
import os

frontend_path = r"..\..\Frontend\src\components\Login.js"

try:
    with open(frontend_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Replace the subtitle
    target_str = '<p className="text-gray-600 mt-2">Compliance Platform</p>'
    new_str = '<p className="text-gray-600 mt-2">Compliance Platform v2.1</p>'
    
    if target_str in content:
        new_content = content.replace(target_str, new_str)
        with open(frontend_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("SUCCESS: Version tag added.")
    else:
        print("WARNING: Could not find target string.")
        # Try finding if already updated
        if "v2.1" in content:
             print("Already updated.")

except Exception as e:
    print(f"Error: {e}")
