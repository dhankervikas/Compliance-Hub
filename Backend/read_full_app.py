
import os

fpath = r"..\..\Frontend\src\App.js"

try:
    with open(fpath, "r", encoding="utf-8") as f:
        print(f.read())
except Exception as e:
    print(f"Error reading App.js: {e}")
