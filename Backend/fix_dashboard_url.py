
import os

fpath = r"..\..\Frontend\src\components\Dashboard.js"

try:
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Target string to verify
    old_def = "const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';"
    new_def = "const API_URL = 'https://assurisk-backend.onrender.com/api/v1';"
    
    if old_def in content:
        new_content = content.replace(old_def, new_def)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("SUCCESS: Replaced API_URL in Dashboard.js")
    else:
        print("WARNING: Exact definition string not found. Trying partial replace...")
        # Fallback partial replace
        if "'http://localhost:8000'" in content:
             new_content = content.replace(" || 'http://localhost:8000'", "")
             # Also replace process.env... if needed, but let's stick to simple first
             # Actually, better to just force the whole line
             # Let's read the file line by line to find the definition
             lines = content.splitlines()
             for i, line in enumerate(lines):
                 if "const API_URL =" in line:
                     lines[i] = new_def
                     print(f"REPLACED Line {i+1}: {new_def}")
             
             with open(fpath, "w", encoding="utf-8") as f:
                 f.write("\n".join(lines))
             print("SUCCESS: Line replacement done.")
        else:
             print("NO CHANGE NEEDED (Localhost string not found).")
             
except Exception as e:
    print(f"Error: {e}")
