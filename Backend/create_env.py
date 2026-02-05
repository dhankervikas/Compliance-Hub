
import os

file_path = r"..\..\Frontend\.env"

content = r"""REACT_APP_API_URL=http://localhost:8000
"""

try:
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"SUCCESS: Created {os.path.abspath(file_path)}")
except Exception as e:
    print(f"ERROR: Failed to create file. {e}")
