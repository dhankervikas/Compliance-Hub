
import subprocess
import os

frontend_dir = r"C:\Users\dhank\OneDrive\Documents\Compliance_Product\Frontend"

print("--- GIT STATUS ---")
try:
    res = subprocess.run(["git", "status"], cwd=frontend_dir, capture_output=True, text=True)
    print(res.stdout)
    print(res.stderr)
except Exception as e:
    print(e)

print("\n--- DASHBOARD.JS CONTENT ---")
try:
    with open(os.path.join(frontend_dir, "src", "components", "Dashboard.js"), "r", encoding="utf-8") as f:
        print(f.read())
except Exception as e:
    print(e)
