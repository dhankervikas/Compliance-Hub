
import os

files = [
    r"..\..\Frontend\src\contexts\AuthContext.js",
    r"..\..\Frontend\src\components\Dashboard.js"
]

login_file = r"..\..\Frontend\src\components\Login.js"

PROD_URL = "https://assurisk-backend.onrender.com"

# 1. Update Auth and Dashboard to hardcoded URL
for file_path in files:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Replace the env line with hardcoded string
        # Regex or simple string search works if exact match, but logic might vary. 
        # I used this line in previous scripts:
        # const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
        
        if "process.env.REACT_APP_API_URL" in content:
            # We replace the whole line logic to be simple
            # Find the line starting with "const API_BASE_URL ="
            lines = content.splitlines()
            new_lines = []
            for line in lines:
                if "const API_BASE_URL =" in line:
                    new_lines.append(f"const API_BASE_URL = '{PROD_URL}'; // Hardcoded for Production")
                else:
                    new_lines.append(line)
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(new_lines))
            print(f"SUCCESS: Hardcoded URL in {os.path.basename(file_path)}")
        else:
            print(f"WARNING: Env variable pattern not found in {os.path.basename(file_path)}")

    except Exception as e:
        print(f"ERROR processing {file_path}: {e}")

# 2. Clean up Login.js debug
try:
    with open(login_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # We want to remove the debug lines I added
    # They look like:
    #     // DEBUGGING: Show the API URL to the user
    #     const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    #     alert(`DEBUG: Your phone is trying to connect to: ${apiUrl}`);
    
    # Using specific unique strings to filter out
    lines = content.splitlines()
    cleaned_lines = []
    for line in lines:
        if "DEBUG:" in line or "process.env.REACT_APP_API_URL" in line:
            continue # Skip debug lines
        cleaned_lines.append(line)
        
    with open(login_file, "w", encoding="utf-8") as f:
        f.write("\n".join(cleaned_lines))
    print(f"SUCCESS: Cleaned debug alerts from Login.js")

except Exception as e:
    print(f"ERROR processing Login.js: {e}")
