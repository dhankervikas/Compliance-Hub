
import sqlite3

DB_PATH = "sql_app.db"

# --- THE STATIC MANIFEST (Source of Truth) ---
# Maps Control ID -> Business Process Name
STATIC_ISO_MAP = {
    # Clause 4: Context
    "4.1": "Governance & Policy", "4.2": "Governance & Policy", "4.3": "Governance & Policy", "4.4": "Governance & Policy",
    
    # Clause 5: Leadership
    "5.1": "Governance & Policy", "5.2": "Governance & Policy", "5.3": "Governance & Policy",
    
    # Clause 6: Planning
    "6.1.1": "Risk Management", "6.1.2": "Risk Management", "6.1.3": "Risk Management",
    "6.2": "Governance & Policy", 
    "6.3": "Governance & Policy", # Explicit User Instruction

    # Clause 7: Support
    "7.1": "Governance & Policy", 
    "7.2": "HR Security", "7.3": "HR Security", 
    "7.4": "Incident & Resilience", # Communication -> Resilience/Response
    "7.5.1": "Governance & Policy", "7.5.2": "Governance & Policy", "7.5.3": "Governance & Policy",

    # Clause 8: Operation
    "8.1": "Risk Management", "8.2": "Risk Management", "8.3": "Risk Management",

    # Clause 9: Performance Eval
    "9.1": "Performance Evaluation", "9.2.1": "Performance Evaluation", "9.2.2": "Performance Evaluation",
    "9.3.1": "Performance Evaluation", "9.3.2": "Performance Evaluation", "9.3.3": "Performance Evaluation",

    # Clause 10: Improvement
    "10.1": "Improvement", "10.2": "Improvement",

    # Annex A.5: Organizational
    "A.5.1": "Governance & Policy", "A.5.2": "Governance & Policy", "A.5.3": "Governance & Policy",
    "A.5.4": "Governance & Policy", "A.5.5": "Governance & Policy", "A.5.6": "Governance & Policy",
    "A.5.7": "Threat Intel",
    "A.5.8": "Governance & Policy",
    "A.5.9": "Asset Management", "A.5.10": "Asset Management", "A.5.11": "Asset Management", 
    "A.5.12": "Asset Management", "A.5.13": "Asset Management",
    "A.5.14": "Network Security",
    "A.5.15": "Access Control (IAM)", "A.5.16": "Access Control (IAM)", "A.5.17": "Access Control (IAM)", "A.5.18": "Access Control (IAM)",
    "A.5.19": "Supplier Mgmt", "A.5.20": "Supplier Mgmt", "A.5.21": "Supplier Mgmt", "A.5.22": "Supplier Mgmt", "A.5.23": "Supplier Mgmt",
    "A.5.24": "Incident & Resilience", "A.5.25": "Incident & Resilience", "A.5.26": "Incident & Resilience", 
    "A.5.27": "Incident & Resilience", "A.5.28": "Incident & Resilience", "A.5.29": "Incident & Resilience", "A.5.30": "Incident & Resilience",
    "A.5.31": "Legal & Compliance", "A.5.32": "Legal & Compliance", "A.5.33": "Legal & Compliance", 
    "A.5.34": "Legal & Compliance", "A.5.35": "Performance Evaluation", "A.5.36": "Legal & Compliance",
    "A.5.37": "Governance & Policy",

    # Annex A.6: People
    "A.6.1": "HR Security", "A.6.2": "HR Security", "A.6.3": "HR Security", "A.6.4": "HR Security",
    "A.6.5": "HR Security", "A.6.6": "HR Security", "A.6.7": "HR Security", "A.6.8": "HR Security",

    # Annex A.7: Physical
    "A.7.1": "Physical Security", "A.7.2": "Physical Security", "A.7.3": "Physical Security", "A.7.4": "Physical Security",
    "A.7.5": "Physical Security", "A.7.6": "Physical Security", "A.7.7": "Physical Security", "A.7.8": "Physical Security",
    "A.7.9": "Physical Security", "A.7.10": "Asset Management", # Storage Media handling
    "A.7.11": "Physical Security", "A.7.12": "Physical Security", "A.7.13": "Physical Security", "A.7.14": "Asset Management", # Removal of assets (Reuse/Disposal)

    # Annex A.8: Technological
    "A.8.1": "Asset Management", # User Endpoint Devices
    "A.8.2": "Access Control (IAM)", "A.8.3": "Access Control (IAM)", "A.8.4": "Access Control (IAM)", "A.8.5": "Access Control (IAM)",
    "A.8.6": "Capacity Management",
    "A.8.7": "Operations (General)",
    "A.8.8": "Vulnerability Management",
    "A.8.9": "Configuration Management",
    "A.8.10": "Operations (General)", "A.8.11": "Operations (General)", "A.8.12": "Operations (General)",
    "A.8.13": "Backup Management", "A.8.14": "Backup Management",
    "A.8.15": "Logging & Monitoring", "A.8.16": "Logging & Monitoring",
    "A.8.17": "Clock Synchronization",
    "A.8.18": "Access Control (IAM)",
    "A.8.19": "SDLC (Development)",
    "A.8.20": "Network Security", "A.8.21": "Network Security", "A.8.22": "Network Security", "A.8.23": "Network Security",
    "A.8.24": "Cryptography",
    "A.8.25": "SDLC (Development)", "A.8.26": "SDLC (Development)", "A.8.27": "SDLC (Development)", 
    "A.8.28": "SDLC (Development)", "A.8.29": "SDLC (Development)", "A.8.30": "SDLC (Development)", "A.8.31": "SDLC (Development)",
    "A.8.32": "Change Management",
    "A.8.33": "Operations (General)", "A.8.34": "Operations (General)"
}

# --- ISO 42001 PREDICTIONS (Prefix-based "Manifest") ---
# Until we have the full static list, we distribute by clause/annex.
ISO42001_PREFIX_MAP = {
    # Clauses
    "ISO42001-4": "AI Strategy & Governance",
    "ISO42001-5": "AI Strategy & Governance",
    "ISO42001-6": "AI Risk Management",
    "ISO42001-7": "AI Strategy & Governance",
    "ISO42001-8": "System Operations (ML Ops)",
    "ISO42001-9": "Performance Evaluation",
    "ISO42001-10": "Improvement",
    
    # Annex A (ISO 42001 Standard Prefixes)
    "ISO42001-A.2": "AI Strategy & Governance",    # Policies
    "ISO42001-A.3": "AI Strategy & Governance",    # Internal Org
    "ISO42001-A.4": "AI Risk Management",          # AI Risk sources
    "ISO42001-A.5": "Data Lifecycle Management",   # Data quality
    "ISO42001-A.6": "Model Development",           # Development Lifecycle
    "ISO42001-A.7": "Third-Party AI Management",   # Third Party
    "ISO42001-A.8": "System Operations (ML Ops)",  # Operation
    "ISO42001-A.9": "Ethics & Responsible AI",     # Communication/Transparency
    "ISO42001-A.10": "Incident & Resilience",      
    
    # Annex A (Alternative "AI-M-" Prefixes found in DB)
    "AI-M-A.2": "AI Strategy & Governance",
    "AI-M-A.3": "AI Strategy & Governance",
    "AI-M-A.4": "AI Risk Management",
    "AI-M-A.5": "Data Lifecycle Management",
    "AI-M-A.6": "Model Development",
    "AI-M-A.7": "Third-Party AI Management",
    "AI-M-A.8": "System Operations (ML Ops)",
    "AI-M-A.9": "Ethics & Responsible AI",
    "AI-M-": "AI Strategy & Governance", # Fallback for AI-M-A.1 / General
}

def reseed_mappings():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("1. Clearing existing mappings...")
    cursor.execute("DELETE FROM process_control_mapping")
    
    print("2. Fetching Mappings Targets...")
    process_map = {}
    cursor.execute("SELECT id, name FROM processes")
    all_procs = cursor.fetchall()
    
    for proc_id, proc_name in all_procs:
        # Default to first subprocess
        cursor.execute("SELECT id FROM sub_processes WHERE process_id = ? ORDER BY id LIMIT 1", (proc_id,))
        sp = cursor.fetchone()
        if sp:
            process_map[proc_name] = sp[0]

    print("3. Generating Mappings (STATIC MANIFEST)...")
    cursor.execute("SELECT id, control_id, category FROM controls")
    controls = cursor.fetchall()
    
    mappings = []
    
    for c_id, c_code, c_cat in controls:
        target_process = None
        
        # 1. Exact Match Lookups (ISO 27001)
        if c_code in STATIC_ISO_MAP:
            target_process = STATIC_ISO_MAP[c_code]
        
        # 2. ISO 42001 / AI Prefix Logic
        elif "ISO42001" in c_code or "AI-M-" in c_code:
            # Sort keys by length desc to match specific first (if we had them), though here mostly same length
            for prefix, process in ISO42001_PREFIX_MAP.items():
                if c_code.startswith(prefix):
                    target_process = process
                    break
            
            # Catch-all for AI if no prefix matched (e.g. AI-X)
            if not target_process:
                target_process = "AI Strategy & Governance"

        # 3. Fallback for unknowns (should be 0 for ISO 27001 now)
        elif "Physical" in str(c_cat): target_process = "Physical Security"
        elif "People" in str(c_cat): target_process = "HR Security"
        elif "Governance" in str(c_cat): target_process = "Governance & Policy"

        if target_process and target_process in process_map:
            sp_id = process_map[target_process]
            mappings.append((sp_id, c_id))
        else:
             # Only warn if it really failed
             if target_process:
                 print(f"[ERROR] Process '{target_process}' not found in DB for {c_code}")
             else:
                 print(f"[WARN] No mapping found for: {c_code}")

    print(f"4. Inserting {len(mappings)} mappings...")
    cursor.executemany("INSERT INTO process_control_mapping (subprocess_id, control_id) VALUES (?, ?)", mappings)
    conn.commit()
    print("Done!")
    conn.close()

if __name__ == "__main__":
    reseed_mappings()
