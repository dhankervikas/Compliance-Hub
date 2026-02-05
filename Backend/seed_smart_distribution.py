
import requests
import sys

BASE_URL = "https://assurisk-backend.onrender.com/api/v1"
AUTH_URL = f"{BASE_URL}/auth/login"
USERNAME = "admin"
PASSWORD = "admin123"

# --- DATASETS --- (Same Framework/Control set as before)
FRAMEWORKS = [
    { "name": "SOC 2 - Trust Services Criteria (2017)", "code": "SOC2_2017", "version": "2017" },
    { "name": "ISO/IEC 27001:2022", "code": "ISO27001_2022", "version": "2022" }
]

# (Full list of controls from previous step, abbreviated here for brevity but logic uses ALL)
# I will use a helper list function to ensure we use the same controls. 
# Actually, to be safe, I'll redefine them fully to avoid "import" errors in this standalone script.

CONTROLS_ISO = [
    # Clause 4
    {"id": "4.1", "cat":"Clause 4"}, {"id": "4.2", "cat":"Clause 4"}, {"id": "4.3", "cat":"Clause 4"}, {"id": "4.4", "cat":"Clause 4"},
    # Clause 5
    {"id": "5.1", "cat":"Clause 5"}, {"id": "5.2", "cat":"Clause 5"}, {"id": "5.3", "cat":"Clause 5"},
    # Clause 6
    {"id": "6.1", "cat":"Clause 6"}, {"id": "6.2", "cat":"Clause 6"}, {"id": "6.3", "cat":"Clause 6"},
    # Clause 7
    {"id": "7.1", "cat":"Clause 7"}, {"id": "7.2", "cat":"Clause 7"}, {"id": "7.3", "cat":"Clause 7"}, {"id": "7.4", "cat":"Clause 7"}, {"id": "7.5", "cat":"Clause 7"},
    # Clause 8
    {"id": "8.1", "cat":"Clause 8"}, {"id": "8.2", "cat":"Clause 8"}, {"id": "8.3", "cat":"Clause 8"},
    # Clause 9
    {"id": "9.1", "cat":"Clause 9"}, {"id": "9.2", "cat":"Clause 9"}, {"id": "9.3", "cat":"Clause 9"},
    # Clause 10
    {"id": "10.1", "cat":"Clause 10"}, {"id": "10.2", "cat":"Clause 10"},

    # Annex A
    {"id": "A.5.1", "cat":"Org"}, {"id": "A.5.7", "cat":"Org"}, {"id": "A.5.9", "cat":"Org"}, {"id": "A.5.10", "cat":"Org"},
    {"id": "A.5.11", "cat":"Org"}, {"id": "A.5.12", "cat":"Org"}, {"id": "A.5.13", "cat":"Org"}, {"id": "A.5.14", "cat":"Org"},
    {"id": "A.5.15", "cat":"Org"}, {"id": "A.5.16", "cat":"Org"}, {"id": "A.5.17", "cat":"Org"}, {"id": "A.5.18", "cat":"Org"},
    {"id": "A.5.19", "cat":"Org"}, {"id": "A.5.20", "cat":"Org"}, {"id": "A.5.21", "cat":"Org"}, {"id": "A.5.22", "cat":"Org"},
    {"id": "A.5.23", "cat":"Org"}, {"id": "A.5.24", "cat":"Org"}, {"id": "A.5.25", "cat":"Org"}, {"id": "A.5.26", "cat":"Org"},
    {"id": "A.5.27", "cat":"Org"}, {"id": "A.5.28", "cat":"Org"}, {"id": "A.5.29", "cat":"Org"}, {"id": "A.5.30", "cat":"Org"},
    {"id": "A.5.31", "cat":"Org"}, {"id": "A.5.37", "cat":"Org"},
    {"id": "A.6.1", "cat":"People"}, {"id": "A.6.2", "cat":"People"}, {"id": "A.6.3", "cat":"People"}, {"id": "A.6.4", "cat":"People"},
    {"id": "A.7.1", "cat":"Physical"}, {"id": "A.7.2", "cat":"Physical"}, {"id": "A.7.3", "cat":"Physical"}, {"id": "A.7.4", "cat":"Physical"},
    {"id": "A.7.5", "cat":"Physical"}, {"id": "A.7.6", "cat":"Physical"}, {"id": "A.7.7", "cat":"Physical"}, {"id": "A.7.8", "cat":"Physical"},
    {"id": "A.7.9", "cat":"Physical"}, {"id": "A.7.10", "cat":"Physical"}, {"id": "A.7.11", "cat":"Physical"}, {"id": "A.7.12", "cat":"Physical"},
    {"id": "A.7.13", "cat":"Physical"}, {"id": "A.7.14", "cat":"Physical"},
    {"id": "A.8.1", "cat":"Tech"}, {"id": "A.8.2", "cat":"Tech"}, {"id": "A.8.3", "cat":"Tech"}, {"id": "A.8.4", "cat":"Tech"},
    {"id": "A.8.5", "cat":"Tech"}, {"id": "A.8.6", "cat":"Tech"}, {"id": "A.8.7", "cat":"Tech"}, {"id": "A.8.8", "cat":"Tech"},
    {"id": "A.8.9", "cat":"Tech"}, {"id": "A.8.10", "cat":"Tech"}, {"id": "A.8.11", "cat":"Tech"}, {"id": "A.8.12", "cat":"Tech"},
    {"id": "A.8.13", "cat":"Tech"}, {"id": "A.8.15", "cat":"Tech"}, {"id": "A.8.16", "cat":"Tech"}, {"id": "A.8.17", "cat":"Tech"},
    {"id": "A.8.19", "cat":"Tech"}, {"id": "A.8.23", "cat":"Tech"}, {"id": "A.8.24", "cat":"Tech"}, {"id": "A.8.25", "cat":"Tech"},
    {"id": "A.8.26", "cat":"Tech"}, {"id": "A.8.27", "cat":"Tech"}, {"id": "A.8.28", "cat":"Tech"}, {"id": "A.8.29", "cat":"Tech"},
    {"id": "A.8.30", "cat":"Tech"}, {"id": "A.8.31", "cat":"Tech"}, {"id": "A.8.32", "cat":"Tech"}, {"id": "A.8.33", "cat":"Tech"},
    {"id": "A.8.34", "cat":"Tech"}
]

CONTROLS_SOC2 = [
    {"id": "CC1.1", "cat": "Security"}, {"id": "CC1.2", "cat": "Security"}, {"id": "CC1.3", "cat": "Security"},
    {"id": "CC2.1", "cat": "Security"}, {"id": "CC3.1", "cat": "Security"}, {"id": "CC3.2", "cat": "Security"},
    {"id": "CC3.3", "cat": "Security"}, {"id": "CC3.4", "cat": "Security"}, {"id": "CC4.1", "cat": "Security"},
    {"id": "CC5.1", "cat": "Security"}, {"id": "CC5.2", "cat": "Security"}, {"id": "CC5.3", "cat": "Security"},
    {"id": "CC6.1", "cat": "Security"}, {"id": "CC6.2", "cat": "Security"}, {"id": "CC6.3", "cat": "Security"},
    {"id": "CC6.4", "cat": "Security"}, {"id": "CC6.5", "cat": "Security"}, {"id": "CC6.6", "cat": "Security"},
    {"id": "CC6.7", "cat": "Security"}, {"id": "CC6.8", "cat": "Security"}, {"id": "CC7.1", "cat": "Security"},
    {"id": "CC7.2", "cat": "Security"}, {"id": "CC7.3", "cat": "Security"}, {"id": "CC7.4", "cat": "Security"},
    {"id": "CC7.5", "cat": "Security"}, {"id": "CC8.1", "cat": "Security"}, {"id": "CC9.1", "cat": "Security"},
    {"id": "CC9.2", "cat": "Security"},
    {"id": "A1.1", "cat": "Availability"}, {"id": "A1.2", "cat": "Availability"}, {"id": "A1.3", "cat": "Availability"},
    {"id": "C1.1", "cat": "Confidentiality"}, {"id": "C1.2", "cat": "Confidentiality"},
    {"id": "P1.0", "cat": "Privacy"}, {"id": "P2.1", "cat": "Privacy"}, {"id": "P3.1", "cat": "Privacy"},
    {"id": "P4.0", "cat": "Privacy"}, {"id": "P5.0", "cat": "Privacy"} 
]

# --- SMART MAPPING LOGIC ---
# Define process structure with keywords for automatic distribution

PROCESS_ROWS = [
    {
        "name": "Governance and control framework",
        "subs": [
            {"name": "Information Security Policy and Standards Management", "keys": ["policy", "5.1", "5.2", "standard"]},
            {"name": "Risk Assessment and Risk Treatment Management", "keys": ["risk", "6.1", "8.2", "cc3"]},
            {"name": "Statement of Applicability and Control Mapping Management", "keys": ["applicability", "mapping"]},
            {"name": "Exceptions and Risk Acceptance Management", "keys": ["exception", "acceptance"]},
            {"name": "Compliance Obligations Management", "keys": ["compliance", "obligation", "legal"]},
            {"name": "Management of Security Metrics and Reporting", "keys": ["metric", "reporting", "9.1"]},
            {"name": "Internal Audit & Management Review", "keys": ["audit", "review", "9.2", "9.3", "4."]}
        ],
        "iso": ["4.1", "4.2", "4.3", "4.4", "5.1", "5.2", "5.3", "6.1", "6.2", "6.3", "9.1", "9.2", "9.3", "10.1", "10.2", "A.5.1", "A.5.7", "A.5.31", "A.5.37"],
        "soc": ["CC1.1", "CC1.2", "CC1.3", "CC2.1", "CC3.1", "CC3.2", "CC3.3", "CC3.4", "CC4.1", "CC5.1"]
    },
    {
        "name": "Asset and information handling",
        "subs": [
            {"name": "Asset Inventory and Ownership Management", "keys": ["inventory", "ownership", "5.9"]},
            {"name": "Information Classification Management", "keys": ["classi", "5.12"]},
            {"name": "Information Labeling and Handling Management", "keys": ["label", "handling"]},
            {"name": "Acceptable Use Management", "keys": ["acceptable", "5.10"]},
            {"name": "Media Handling and Secure Disposal Management", "keys": ["media", "disposal", "disk"]},
            {"name": "Information Transfer Management", "keys": ["transfer", "5.14"]},
            {"name": "Records Retention and Secure Disposal Management", "keys": ["retention", "record", "archive"]},
            {"name": "Data Masking & Information Deletion", "keys": ["masking", "deletion"]}
        ],
        "iso": ["A.5.9", "A.5.10", "A.5.11", "A.5.12", "A.5.13", "A.5.14", "A.7.10", "A.8.10", "A.8.11", "A.8.12", "A.8.13"],
        "soc": ["CC6.1", "CC6.8", "CC7.1"]
    },
    {
        "name": "Identity and access",
        "subs": [
             {"name": "Identity Lifecycle Management (JML)", "keys": ["lifecycle", "jml", "joiner", "leaver"]},
             {"name": "Access Management (Request, Approve, Provision, Remove)", "keys": ["request", "provision", "5.15"]},
             {"name": "Privileged Access Management (PAM)", "keys": ["privilege", "admin", "8.2"]},
             {"name": "Authentication and Credential Management (MFA/Secrets)", "keys": ["auth", "credential", "mfa", "secret", "5.17"]},
             {"name": "Access Review and Recertification Management", "keys": ["review", "recertification", "5.18"]},
             {"name": "Segregation of Duties Management", "keys": ["segregation", "duties", "5.3"]}
        ],
        "iso": ["A.5.15", "A.5.16", "A.5.17", "A.5.18", "A.8.2", "A.8.3", "A.8.4", "A.8.5"],
        "soc": ["CC6.1", "CC6.2", "CC6.3", "CC6.6"]
    },
    {
        "name": "Supplier and third-party security",
        "subs": [
           {"name": "Supplier Security Due Diligence and Onboarding", "keys": ["diligence", "onboard"]},
           {"name": "Supplier Security Requirements and Contract Management", "keys": ["contract", "requirement", "5.20"]},
           {"name": "ICT Supply Chain Security Management", "keys": ["supply chain", "5.21"]},
           {"name": "Supplier Service Monitoring and Assurance", "keys": ["monitoring", "assurance", "5.22"]},
           {"name": "Supplier Change and Offboarding Management", "keys": ["change", "offboard"]},
           {"name": "Cloud Service Security", "keys": ["cloud", "5.23", "cc9"]}
        ],
        "iso": ["A.5.19", "A.5.20", "A.5.21", "A.5.22", "A.5.23"],
        "soc": ["CC9.2"]
    },
    {
        "name": "Security operations",
        "subs": [
           {"name": "Security Event Logging Management", "keys": ["log", "event", "8.15"]},
           {"name": "Security Monitoring and Alert Handling (SOC)", "keys": ["monitor", "alert", "soc", "8.16"]},
           {"name": "Malware Protection Management", "keys": ["malware", "virus", "8.7"]},
           {"name": "Vulnerability Management (Scan, Assess, Remediate)", "keys": ["vulnerability", "scan", "8.8"]},
           {"name": "Patch Management", "keys": ["patch", "update"]},
           {"name": "Secure Configuration and Hardening Management", "keys": ["config", "harden", "8.9"]},
           {"name": "Change Management", "keys": ["change", "8.32"]},
           {"name": "Backup Management", "keys": ["backup", "8.13"]},
           {"name": "Recovery and Restoration Testing Management", "keys": ["recovery", "restore"]},
           {"name": "Capacity and Performance Management", "keys": ["capacity", "performance", "8.6"]},
           {"name": "Time Synchronization Management", "keys": ["time", "ntp", "8.17"]}
        ],
        "iso": ["A.8.1", "A.8.5", "A.8.6", "A.8.7", "A.8.8", "A.8.9", "A.8.15", "A.8.16", "A.8.17", "A.8.19", "A.8.23", "A.8.32"],
        "soc": ["CC7.1", "CC7.2", "CC8.1"]
    },
    {
        "name": "Incident and resilience",
        "subs": [
            {"name": "Information Security Incident Management", "keys": ["incident", "5.24"]},
            {"name": "Evidence Handling and Forensic Readiness Management", "keys": ["evidence", "forensic", "5.28"]},
            {"name": "Business Continuity and ICT Readiness Management", "keys": ["continuity", "bcp", "5.29", "5.30"]},
            {"name": "Crisis Communication and Stakeholder Notification", "keys": ["communication", "crisis", "notification"]},
            {"name": "Lessons Learned and Post-incident Improvement", "keys": ["lesson", "improvement", "5.25"]}
        ],
        "iso": ["A.5.24", "A.5.25", "A.5.26", "A.5.27", "A.5.28", "A.5.29", "A.5.30"],
        "soc": ["CC7.3", "CC7.4", "CC7.5", "CC9.1"]
    },
    {
        "name": "Physical and environmental security",
        "subs": [
             {"name": "Physical Access Management (Badges/Visitors)", "keys": ["access", "badge", "visitor", "7.2"]},
             {"name": "Secure Areas Management (Zoning/Monitoring)", "keys": ["zone", "area", "7.3"]},
             {"name": "Physical Security Monitoring Management (CCTV)", "keys": ["cctv", "monitor", "7.4"]},
             {"name": "Equipment Siting, Protection, and Maintenance", "keys": ["equipment", "siting", "maintenance", "7.8"]},
             {"name": "Secure Disposal or Reuse of Equipment Management", "keys": ["disposal", "reuse", "7.14"]},
             {"name": "Environmental Threat Protection Management", "keys": ["environment", "threat", "7.5"]}
        ],
        "iso": ["A.7.1", "A.7.2", "A.7.3", "A.7.4", "A.7.5", "A.7.6", "A.7.7", "A.7.8", "A.7.9", "A.7.11", "A.7.12", "A.7.13", "A.7.14"],
        "soc": ["CC6.4"]
    },
    {
        "name": "Secure engineering and technology lifecycle",
        "subs": [
             {"name": "Secure System Acquisition and Security-by-Design", "keys": ["acquisition", "design", "8.25"]},
             {"name": "Secure Development Lifecycle Management (SDLC)", "keys": ["sdlc", "development", "8.25"]},
             {"name": "Application Security Testing Management (SAST/DAST)", "keys": ["testing", "sast", "dast", "8.29"]},
             {"name": "Release and Deployment Security Management", "keys": ["release", "deploy"]},
             {"name": "Source Code and Build Pipeline Security Management", "keys": ["source", "code", "pipeline"]},
             {"name": "Test Data Management", "keys": ["test data", "8.31"]},
             {"name": "Cloud Security Configuration Management", "keys": ["cloud", "config"]},
             {"name": "Encryption and Key Management", "keys": ["encryption", "key", "8.24", "10."]},
             {"name": "Data Masking and Data Loss Prevention Management", "keys": ["dlp", "loss", "masking"]} 
        ],
        "iso": ["A.8.24", "A.8.25", "A.8.26", "A.8.27", "A.8.28", "A.8.29", "A.8.30", "A.8.31", "A.8.33", "A.8.34"],
        "soc": ["CC8.1", "CC6.1", "CC6.7"]
    }
]

def get_token():
    print(f"Logging in as {USERNAME}...")
    try:
        resp = requests.post(AUTH_URL, data={"username": USERNAME, "password": PASSWORD})
        if resp.status_code == 200:
            return resp.json().get("access_token")
        else:
            print(f"Login failed: {resp.text}")
            sys.exit(1)
    except Exception as e:
        print(f"Connection error: {e}")
        sys.exit(1)

def seed():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # 1. Frameworks
    print("\n--- 1. Syncing Frameworks ---")
    fw_map = {} 
    for fw in FRAMEWORKS:
        resp = requests.post(f"{BASE_URL}/frameworks/", json=fw, headers=headers)
        if resp.status_code in [200, 201]:
             fw_data = resp.json()
             fw_map[fw["code"]] = fw_data["id"] 
        elif resp.status_code == 409 or "already exists" in resp.text:
             all_fw = requests.get(f"{BASE_URL}/frameworks/", headers=headers).json()
             existing = next(f for f in all_fw if f["code"] == fw["code"])
             fw_map[fw["code"]] = existing["id"]
    print(f"Frameworks Ready: {fw_map}")

    # 2. Controls
    print("\n--- 2. Syncing Controls ---")
    control_db_map = {} 

    def seed_controls(ctrl_list, fw_code):
        if fw_code not in fw_map: return
        fw_id = fw_map[fw_code]
        for c in ctrl_list:
            c_payload = {
                "control_id": c["id"],
                "title": f" Requirement {c['id']}" if "." in c["id"] and len(c["id"]) < 5 else f"Control {c['id']}", 
                "description": f"Standard requirements for {c['cat']}",
                "category": c["cat"],
                "priority": "high",
                "framework_id": fw_id
            }
            requests.post(f"{BASE_URL}/controls/", json=c_payload, headers=headers)
            
    seed_controls(CONTROLS_SOC2, "SOC2_2017")
    seed_controls(CONTROLS_ISO, "ISO27001_2022")
    
    # Bulk Fetch
    print("Fetching Control IDs...")
    all_c = requests.get(f"{BASE_URL}/controls/?limit=3000", headers=headers).json()
    for c in all_c:
        control_db_map[c["control_id"]] = c["id"]
    
    # 3. Processes & Smart Mapping
    print("\n--- 3. Process Hierarchy (SMART DISTRIBUTION) ---")
    
    # Cleanup old processes
    all_procs = requests.get(f"{BASE_URL}/processes/", headers=headers).json()
    for p in all_procs:
        try:
             requests.delete(f"{BASE_URL}/processes/{p['id']}", headers=headers)
        except: pass

    for row in PROCESS_ROWS:
        p_name = row["name"]
        print(f"\nCreated Process: {p_name}")
        
        # Create Process & Subprocesses
        payload = {
            "name": p_name,
            "description": "Process Group",
            "sub_processes": [{"name": sub["name"], "description": "Activity"} for sub in row["subs"]]
        }
        
        resp = requests.post(f"{BASE_URL}/processes/", json=payload, headers=headers)
        if resp.status_code not in [200, 201]:
            continue
        
        p_data = resp.json()
        
        # --- SMART DISTRIBUTION LOGIC ---
        # Get DB IDs for created sub-processes
        sp_map = {sp["name"]: sp["id"] for sp in p_data["sub_processes"]}
        
        # Distribution Plan: {sp_id: [control_ids]}
        distribution = {sp_id: [] for sp_id in sp_map.values()}
        
        # Controls to process for this row
        controls_to_map = row["iso"] + row["soc"]
        
        for c_code in controls_to_map:
            if c_code not in control_db_map: continue
            
            c_id = control_db_map[c_code]
            
            # Find best match sub-process
            best_sp_id = None
            
            # 1. Try Keyword Match
            for sub_def in row["subs"]:
                sp_name = sub_def["name"]
                
                # Check for ID match (e.g. "5.1" matches "5.1")
                for key in sub_def["keys"]:
                    if key.lower() in c_code.lower():
                        best_sp_id = sp_map[sp_name]
                        break
                if best_sp_id: break
                
                # Check for Control Title match? (Not using detailed titles here, just IDs and basic logic)
            
            # 2. Fallback to First sub-process if no keyword match
            if not best_sp_id:
                first_sp_name = row["subs"][0]["name"]
                best_sp_id = sp_map[first_sp_name]
            
            # Assign
            distribution[best_sp_id].append(c_id)
            
        # Execute Mappings
        for sp_id, c_ids in distribution.items():
            if c_ids:
                requests.post(
                     f"{BASE_URL}/processes/subprocess/{sp_id}/map-controls",
                     json={"control_ids": list(set(c_ids))}, # de-dupe just in case
                     headers=headers
                )
                print(f"    -> {len(c_ids)} controls mapped to Sub-Process #{sp_id}")

if __name__ == "__main__":
    seed()
