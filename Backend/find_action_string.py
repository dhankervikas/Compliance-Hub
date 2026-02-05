import os

search_dir = r"C:\Users\dhank\OneDrive\Documents\Compliance_Product"
search_string = "Securely Dispose of Sensitive Data"

print(f"Searching for string '{search_string}' in {search_dir}...")

files_with_string = []

for root, dirs, files in os.walk(search_dir):
    if ".pytest_cache" in root or "node_modules" in root or ".git" in root:
        continue
        
    for file in files:
        if file.endswith((".csv", ".txt", ".py", ".md", ".json")): # Skip .xlsx for text search unless using openpyxl
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    if search_string in content:
                        files_with_string.append(path)
            except Exception:
                pass

print(f"Found {len(files_with_string)} matching files.")
for f in files_with_string:
    print(f"[MATCH] {f}")
