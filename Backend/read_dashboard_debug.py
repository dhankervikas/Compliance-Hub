
import os

target_path = r"..\..\Frontend\src\components\Dashboard.js"

try:
    with open(target_path, "r", encoding="utf-8") as f:
        print(f.read())
except Exception as e:
    print(f"Error: {e}")
