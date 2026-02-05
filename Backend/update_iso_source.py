
import json
from app.utils.iso_data import ISO_CONTROLS_DATA

# 1. Define Missing Data
missing_7_5 = [
    {
        "control_id": "7.5.1",
        "title": "Documented information - General",
        "description": "The organization's information security management system shall include: a) documented information required by this document; and b) documented information determined by the organization as being necessary for the effectiveness of the information security management system.",
        "category": "Governance",
        "priority": "medium",
        "classification": "MANUAL"
    },
    {
        "control_id": "7.5.2",
        "title": "Creating and updating",
        "description": "When creating and updating documented information the organization shall ensure appropriate: a) identification and description (e.g. a title, date, author, or reference number); b) format (e.g. language, software version, graphics) and media (e.g. paper, electronic); and c) review and approval for suitability and adequacy.",
        "category": "Governance",
        "priority": "medium",
        "classification": "MANUAL"
    },
    {
        "control_id": "7.5.3",
        "title": "Control of documented information",
        "description": "Documented information required by the information security management system and by this document shall be controlled to ensure: a) it is available and suitable for use, where and when it is needed; and b) it is adequately protected (e.g. from loss of confidentiality, improper use, or loss of integrity).",
        "category": "Governance",
        "priority": "high",
        "classification": "MANUAL"
    }
]

missing_9_2 = [
    {
        "control_id": "9.2.1",
        "title": "Internal audit - General",
        "description": "The organization shall conduct internal audits at planned intervals to provide information on whether the information security management system: a) conforms to 1) the organization’s own requirements for its information security management system; 2) the requirements of this document; b) is effectively implemented and maintained.",
        "category": "Performance Evaluation",
        "priority": "high",
        "classification": "MANUAL"
    },
    {
        "control_id": "9.2.2",
        "title": "Internal audit programme",
        "description": "The organization shall plan, establish, implement and maintain an audit programme(s), including the frequency, methods, responsibilities, planning requirements and reporting. The audit programme(s) shall take into consideration the importance of the processes concerned and the results of previous audits.",
        "category": "Performance Evaluation",
        "priority": "high",
        "classification": "MANUAL"
    }
]

missing_9_3 = [
    {
        "control_id": "9.3.1",
        "title": "Management review - General",
        "description": "Top management shall review the organization's information security management system at planned intervals to ensure its continuing suitability, adequacy and effectiveness.",
        "category": "Performance Evaluation",
        "priority": "high",
        "classification": "MANUAL"
    },
    {
        "control_id": "9.3.2",
        "title": "Management review inputs",
        "description": "The management review shall include consideration of: a) the status of actions from previous management reviews; b) changes in external and internal issues that are relevant to the information security management system; c) feedback on the information security performance, including trends in...",
        "category": "Performance Evaluation",
        "priority": "high",
        "classification": "MANUAL"
    },
    {
        "control_id": "9.3.3",
        "title": "Management review results",
        "description": "The results of the management review shall include decisions related to continual improvement opportunities and any needs for changes to the information security management system.",
        "category": "Performance Evaluation",
        "priority": "high",
        "classification": "MANUAL"
    }
]

# 2. Modify Data Structure
new_data = []
ids_to_remove = ["7.5", "9.2", "9.3"]

for control in ISO_CONTROLS_DATA:
    cid = control["control_id"]
    
    # Skip if replaced
    if cid in ids_to_remove:
        continue
        
    # Inject 7.5.x after 7.4
    if cid == "7.4":
        new_data.append(control)
        new_data.extend(missing_7_5)
        # Skip appending control again (already done)
        continue
    
    # Inject 9.2.x after 9.1
    if cid == "9.1":
        new_data.append(control)
        new_data.extend(missing_9_2)
        continue

    # Inject 9.3.x (Which was removed, so we need to inject after 9.2.2 which is now in the list... wait)
    # The logic above for 7.4 and 9.1 handles "Appending after".
    # But 9.3 is its own block. 
    # Let's simple check: if next item was 9.3, we insert missing_9_3.
    # Actually, simpler: just populate new_data and sort later? No, order matters.
    
    new_data.append(control)

# 9.3 replacement needs to happen. 
# My loop removed 9.3. I need to insert 9.3.x where 9.3 WAS.
# Let's refine logical insertion.

final_data = []
for control in ISO_CONTROLS_DATA:
    cid = control["control_id"]
    
    if cid == "7.5":
        final_data.extend(missing_7_5)
    elif cid == "9.2":
        final_data.extend(missing_9_2)
    elif cid == "9.3":
        final_data.extend(missing_9_3)
    else:
        final_data.append(control)

# 3. Add Domain Logic
for control in final_data:
    cid = control["control_id"]
    domain = "Uncategorized"
    
    if cid.startswith("4."): domain = "Clause 4: Context of the Organization"
    elif cid.startswith("5."): domain = "Clause 5: Leadership"
    elif cid.startswith("6."): domain = "Clause 6: Planning"
    elif cid.startswith("7."): domain = "Clause 7: Support"
    elif cid.startswith("8."): domain = "Clause 8: Operation"
    elif cid.startswith("9."): domain = "Clause 9: Performance Evaluation"
    elif cid.startswith("10."): domain = "Clause 10: Improvement"
    elif cid.startswith("A.5."): domain = "Annex A.5: Organizational Controls"
    elif cid.startswith("A.6."): domain = "Annex A.6: People Controls"
    elif cid.startswith("A.7."): domain = "Annex A.7: Physical Controls"
    elif cid.startswith("A.8."): domain = "Annex A.8: Technological Controls"
    
    control["domain"] = domain

# 4. Generate Python File Content
output_str = "ISO_CONTROLS_DATA = [\n"
for item in final_data:
    output_str += "    {\n"
    for k, v in item.items():
        if isinstance(v, str):
            # Escape quotes
            safe_v = v.replace('"', '\\"')
            output_str += f'        "{k}": "{safe_v}",\n'
        else:
             output_str += f'        "{k}": {v},\n'
    output_str += "    },\n"
output_str += "]\n"

with open("app/utils/iso_data.py", "w", encoding="utf-8") as f:
    f.write(output_str)

print("[+] Successfully updated ISO_CONTROLS_DATA with domains and missing sub-clauses.")
