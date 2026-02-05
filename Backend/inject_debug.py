
import os

file_path = r"..\..\Frontend\src\components\Login.js"

# Read existing content first to be safe, but since I know the structure, I'll rewrite the component part I need
# Actually, safer to read and replace just the useEffect block using string replacement

try:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Target just the start of the useEffect
    target = "  useEffect(() => {"
    
    # New content includes the alert at the top of the effect
    replacement = """  useEffect(() => {
    // DEBUGGING: Show the API URL to the user
    // const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    // alert(`DEBUG: Connnecting to: ${apiUrl}`);"""

    if target in content and "DEBUG:" not in content:
        new_content = content.replace(target, replacement, 1)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"SUCCESS: Injected debug alert into {os.path.abspath(file_path)}")
    elif "DEBUG:" in content:
        print("Alert already injected.")
    else:
        print("ERROR: Target signature not found.")
        print(content[:500])

except Exception as e:
    print(f"ERROR: {e}")
