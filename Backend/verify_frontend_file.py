
import os

target_path = r"..\..\Frontend\src\components\FrameworkDetail.js"

try:
    with open(target_path, "r", encoding="utf-8") as f:
        content = f.read()
        if "Audit timeline" in content:
            print("VERIFIED: Premium UI code is present on disk.")
        else:
            print("FAILED: Old code detected.")
            print("First 100 chars:", content[:100])
except Exception as e:
    print(f"Error: {e}")
