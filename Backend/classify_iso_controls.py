import re

# CLASSIFICATION LOGIC
# A.8 -> Technological -> [AUTO]
# A.6 -> People -> [HYBRID]
# A.5, A.7, Clauses -> [MANUAL]

# Read iso_data.py
file_path = r"C:\Projects\Compliance_Product\Backend\app\utils\iso_data.py"
with open(file_path, "r") as f:
    content = f.read()

new_lines = []
lines = content.split('\n')
current_id = None
current_classification = None

for line in lines:
    # 1. Capture Control ID
    id_match = re.search(r'"control_id":\s+"([^"]+)"', line)
    if id_match:
        current_id = id_match.group(1)
        # Determine Classification
        if current_id.startswith("A.8"):
            current_classification = "AUTO"
        elif current_id.startswith("A.6"):
            current_classification = "HYBRID"
        else:
            current_classification = "MANUAL"
        
        new_lines.append(line)
        continue
    
    # 2. Add Classification after Priority
    if '"priority":' in line:
        new_lines.append(line)
        # Add new fields
        indent = line.split('"')[0]
        new_lines.append(f'{indent}"classification": "{current_classification}",')
        print(f"Added {current_classification} to {current_id}")
        continue
    
    # Clean up any existing classification/automation fields if re-running
    if '"classification":' in line:
        continue

    new_lines.append(line)

# Write back
with open(file_path, "w") as f:
    f.write('\n'.join(new_lines))

print("Done updating iso_data.py with Classifications!")
