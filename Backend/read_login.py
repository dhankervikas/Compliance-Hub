
import os

frontend_path = r"..\..\Frontend\src\components\Login.js"

try:
    with open(frontend_path, "r", encoding="utf-8") as f:
        print(f.read())
except Exception as e:
    print(f"Error: {e}")
