
import os

files = [
    r"..\..\Frontend\src\components\FrameworkDetail.js",
    r"..\..\Frontend\src\contexts\AuthContext.js",
    r"..\..\Frontend\src\components\Dashboard.js"
]

print("--- AUDITING API URLs ---")
for fpath in files:
    try:
        if not os.path.exists(fpath):
            print(f"FILE: {os.path.basename(fpath)} (NOT FOUND)")
            continue

        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
            print(f"\nFILE: {os.path.basename(fpath)}")
            # Simple check for the hardcoded URL
            if "https://assurisk-backend.onrender.com" in content:
                print("STATUS: [OK] Contains Production URL")
            else:
                print("STATUS: [FAIL] MISSING Production URL")
            
            # Check for localhost
            if "localhost" in content:
                 print("WARNING: [WARN] Contains 'localhost'")
            else:
                 print("CLEAN: No 'localhost' found")
                 
            # Print the line defining API_URL if possible
            for line in content.splitlines():
                if "const API_URL =" in line or "axios.defaults.baseURL =" in line:
                    print(f"DEFINITION: {line.strip()}")

    except Exception as e:
        print(f"Error reading {fpath}: {e}")
