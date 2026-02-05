
file_path = r"C:\Projects\Compliance_Product\Backend\app\utils\iso_data.py"

with open(file_path, "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    stripped = line.rstrip()
    # Check if line contains priority and doesn't end with comma
    if '"priority":' in line and not stripped.endswith(","):
        # preserve indentation and add comma
        new_lines.append(stripped + ",\n")
    else:
        new_lines.append(line)

with open(file_path, "w") as f:
    f.writelines(new_lines)

print("Fixed syntax errors in iso_data.py")
