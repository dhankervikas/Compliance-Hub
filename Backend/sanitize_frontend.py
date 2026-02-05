
import os

files = [
    r"..\..\Frontend\src\contexts\AuthContext.js",
    r"..\..\Frontend\src\components\Dashboard.js"
]

target_url = "const API_URL = 'https://assurisk-backend.onrender.com/api/v1';"

print("--- SANITIZING FRONTEND URLs ---")
for fpath in files:
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        new_lines = []
        replaced = False
        for line in lines:
            if "const API_URL =" in line or "axios.defaults.baseURL =" in line:
                new_lines.append(f"{target_url}\n")
                replaced = True
                print(f"REPLACED line in {os.path.basename(fpath)}")
            else:
                new_lines.append(line)
        
        if replaced:
            with open(fpath, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            print(f"SAVED: {os.path.basename(fpath)}")
        else:
            print(f"NO CHANGE: {os.path.basename(fpath)}")

    except Exception as e:
        print(f"Error processing {fpath}: {e}")
