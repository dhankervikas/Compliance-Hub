import pandas as pd
import os

# Source Files
INTENT_LIB = r"C:\Projects\Compliance_Product\Backend\iso27001_intent_library.csv"
OUTPUT_FILE = r"C:\Projects\Compliance_Product\Backend\MASTER_ISO27001_INTENTS.csv"

# Mapping Logic (From remap_iso27001_processes.py)
MAPPING_RULES = {
    "A.5": "Governance & Policy",
    "A.6": "Governance & Policy", 
    "A.7": "HR Security",
    "A.8": "Asset Management",
    "A.9": "Access Control (IAM)",
    "A.10": "Cryptography",
    "A.11": "Physical Security",
    "A.12.1": "Operations (General)",
    "A.12.2": "Operations (General)",
    "A.12.3": "Backup Management", 
    "A.12.4": "Logging & Monitoring",
    "A.12.5": "Operations (General)",
    "A.12.6": "Vulnerability Management",
    "A.12.7": "Operations (General)",
    "A.13": "Network Security",
    "A.14": "SDLC (Development)",
    "A.15": "Supplier Mgmt",
    "A.16": "Incident & Resilience",
    "A.17": "Incident & Resilience",
    "A.18": "Legal & Compliance",
    # Clauses
    "4.": "Governance & Policy",
    "5.": "Governance & Policy",
    "6.": "Risk Management",
    "7.": "Governance & Policy",
    "8.": "Operations (General)",
    "9.": "Internal Audit",
    "10.": "Improvement"
}

# Actionable Title Map (from processes.py + others if found)
ACTIONABLE_TITLES = {
    "A.5.15": "Enforce Least-Privilege Access Reviews",
    "A.8.10": "Securely Dispose of Sensitive Data",
    "A.5.1": "Establish Information Security Policies",
    "A.5.3": "Segregate Conflicting Duties",
    "A.6.1": "Screen Employees Prior to Employment",
    "A.8.2": "Classify Information Assets",
    "A.12.1": "Document Operating Procedures"
}

def get_process(clause_id):
    if not isinstance(clause_id, str):
        return "Uncategorized"
    
    sorted_rules = sorted(MAPPING_RULES.items(), key=lambda x: len(x[0]), reverse=True)
    
    for prefix, process in sorted_rules:
        if clause_id.startswith(prefix):
            return process
            
    return "Uncategorized"

def get_action_title(row):
    cid = row['Clause_or_control']
    if cid in ACTIONABLE_TITLES:
        return ACTIONABLE_TITLES[cid]
    
    # Fallback: Use Intent Statement if available, otherwise "Implement [Control]"
    intent = str(row.get('Intent_statement', '')).strip()
    if intent and intent.lower() != 'nan':
         return intent
    
    return f"Implement {cid}"

def reconstruct_master():
    print(f"Reading {INTENT_LIB}...")
    try:
        df = pd.read_csv(INTENT_LIB, encoding='latin1')
    except Exception as e:
        print(f"Failed to read CSV: {e}")
        return

    print(f"Loaded {len(df)} rows.")
    
    # Apply Process Mapping
    print("Applying 'Process' mapping...")
    df['Process'] = df['Clause_or_control'].apply(get_process)
    
    # Apply Action Title Mapping
    print("Applying 'Action_Title' translation...")
    df['Action_Title'] = df.apply(get_action_title, axis=1)
    
    # Add status if missing
    if 'compliance_status' not in df.columns:
        print("Adding 'compliance_status' column (default: 'Not Started')...")
        df['compliance_status'] = 'Not Started'
        
    # Verify Internal Audit separation
    audit_count = len(df[df['Process'] == 'Internal Audit'])
    print(f"Internal Audit Items: {audit_count}")
    
    # Save
    print(f"Saving to {OUTPUT_FILE}...")
    df.to_csv(OUTPUT_FILE, index=False)
    print("Done.")

if __name__ == "__main__":
    reconstruct_master()
