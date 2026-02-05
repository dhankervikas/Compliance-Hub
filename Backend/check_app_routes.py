
import os

fpath = r"..\..\Frontend\src\App.js"

try:
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    
    print("\n--- CHECKING APP.JS ---")
    if "PlaceholderPage" in content:
        print("STATUS: PlaceholderPage FOUND")
    else:
        print("STATUS: PlaceholderPage MISSING")

    if "/controls" in content:
        print("STATUS: Route /controls FOUND")
    else:
        print("STATUS: Route /controls MISSING")
        
    print("\n--- CONTENT SNIPPET ---")
    print(content[-500:]) # Print last 500 chars to see routes

except Exception as e:
    print(f"Error reading App.js: {e}")
