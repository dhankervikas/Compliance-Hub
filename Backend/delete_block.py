
import os

file_path = r"C:\Projects\Compliance_Product\Frontend\src\components\FrameworkDetail.js"

with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Deleting lines 1081 to 1171 (1-indexed)
# 0-indexed: 1080 to 1170 (inclusive)
# Slice [1080:1171] covers indices 1080, ..., 1170.

print(f"Deleting lines 1081-1171. First line to delete: {lines[1080].strip()}")
print(f"Last line to delete: {lines[1170].strip()}")
print(f"Next line (kept): {lines[1171].strip()}")

del lines[1080:1171]

with open(file_path, "w", encoding="utf-8") as f:
    f.writelines(lines)

print("Done.")
