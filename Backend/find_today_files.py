import os
import datetime
import glob

search_dir = r"C:\Projects\Compliance_Product\Backend"
target_date = datetime.date(2026, 2, 3)

print(f"Searching for files modified on {target_date} in {search_dir}...")

found_files = []
for root, dirs, files in os.walk(search_dir):
    if "venv" in root or "__pycache__" in root:
        continue
    for file in files:
        path = os.path.join(root, file)
        try:
            mtime = datetime.date.fromtimestamp(os.path.getmtime(path))
            if mtime == target_date:
                size = os.path.getsize(path)
                found_files.append((path, size))
        except Exception as e:
            pass

# Sort by size descending (Master file likely large)
found_files.sort(key=lambda x: x[1], reverse=True)

print(f"Found {len(found_files)} files modified today.")
for f, s in found_files[:30]:
    print(f"[{s} B] {os.path.basename(f)}")
