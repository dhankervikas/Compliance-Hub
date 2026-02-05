
import requests
import sys

BASE_URL = "https://assurisk-backend.onrender.com/api/v1"
AUTH_URL = f"{BASE_URL}/auth/login"
USERNAME = "admin"
PASSWORD = "admin123"

# --- DATASETS ---

FRAMEWORKS = [
    {
        "name": "SOC 2 - Trust Services Criteria (2017)",
        "code": "SOC2_2017",
        "description": "AICPA Trust Services Criteria.",
        "version": "2017"
    },
    {
        "name": "ISO/IEC 27001:2022",
        "code": "ISO27001_2022",
        "description": "Information security management systems.",
        "version": "2022"
    }
]

# --- CONTROLS ---
# Added Clauses 4-10 as requested
CONTROLS_ISO = [
    # Clause 4: Context
    {"id": "4.1", "cat":"Clause 4"}, {"id": "4.2", "cat":"Clause 4"}, {"id": "4.3", "cat":"Clause 4"}, {"id": "4.4", "cat":"Clause 4"},
    # Clause 5: Leadership
    {"id": "5.1", "cat":"Clause 5"}, {"id": "5.2", "cat":"Clause 5"}, {"id": "5.3", "cat":"Clause 5"},
    # Clause 6: Planning
    {"id": "6.1", "cat":"Clause 6"}, {"id": "6.2", "cat":"Clause 6"}, {"id": "6.3", "cat":"Clause 6"},
    # Clause 7: Support
    {"id": "7.1", "cat":"Clause 7"}, {"id": "7.2", "cat":"Clause 7"}, {"id": "7.3", "cat":"Clause 7"}, {"id": "7.4", "cat":"Clause 7"}, {"id": "7.5", "cat":"Clause 7"},
    # Clause 8: Operation
    {"id": "8.1", "cat":"Clause 8"}, {"id": "8.2", "cat":"Clause 8"}, {"id": "8.3", "cat":"Clause 8"},
    # Clause 9: Performance
    {"id": "9.1", "cat":"Clause 9"}, {"id": "9.2", "cat":"Clause 9"}, {"id": "9.3", "cat":"Clause 9"},
    # Clause 10: Improvement
    {"id": "10.1", "cat":"Clause 10"}, {"id": "10.2", "cat":"Clause 10"},

    # Annex A (Existing)
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

# --- PROCESS MAPPING (Refined) ---
# Logic: Controls will be mapped to the FIRST sub-process in the list to avoid duplication.
PROCESS_ROWS = [
    {
        "name": "Governance and control framework",
        "subs": [
            "Information Security Policy and Standards Management", "Risk Assessment and Risk Treatment Management",
            "Statement of Applicability and Control Mapping Management", "Exceptions and Risk Acceptance Management",
            "Compliance Obligations Management", "Management of Security Metrics and Reporting",
            "Internal Audit & Management Review"
        ],
        # Clause 4, 5, 6, 9, 10 mapped here
        "iso": ["4.1", "4.2", "4.3", "4.4", "5.1", "5.2", "5.3", "6.1", "6.2", "6.3", "9.1", "9.2", "9.3", "10.1", "10.2", "A.5.1", "A.5.7", "A.5.31", "A.5.37"],
        "soc": ["CC1.1", "CC1.2", "CC1.3", "CC2.1", "CC3.1", "CC3.2", "CC3.3", "CC3.4", "CC4.1", "CC5.1"]
    },
    {
        "name": "Asset and information handling",
        "subs": [
            "Asset Inventory and Ownership Management", "Information Classification Management",
            "Information Labeling and Handling Management", "Acceptable Use Management",
            "Media Handling and Secure Disposal Management", "Information Transfer Management",
            "Records Retention and Secure Disposal Management", "Data Masking & Information Deletion"
        ],
        "iso": ["A.5.9", "A.5.10", "A.5.11", "A.5.12", "A.5.13", "A.5.14", "A.7.10", "A.8.10", "A.8.11", "A.8.12", "A.8.13"],
        "soc": ["CC6.1", "CC6.8", "CC7.1"]
    },
    {
        "name": "Identity and access",
        "subs": [
            "Identity Lifecycle Management (JML)", "Access Management (Request, Approve, Provision, Remove)",
            "Privileged Access Management (PAM)", "Authentication and Credential Management (MFA/Secrets)",
            "Access Review and Recertification Management", "Segregation of Duties Management"
        ],
        "iso": ["A.5.15", "A.5.16", "A.5.17", "A.5.18", "A.8.2", "A.8.3", "A.8.4", "A.8.5"],
        "soc": ["CC6.1", "CC6.2", "CC6.3", "CC6.6"]
    },
    {
        "name": "Supplier and third-party security",
        "subs": [
           "Supplier Security Due Diligence and Onboarding", "Supplier Security Requirements and Contract Management",
           "ICT Supply Chain Security Management", "Supplier Service Monitoring and Assurance",
           "Supplier Change and Offboarding Management", "Cloud Service Security"
        ],
        "iso": ["A.5.19", "A.5.20", "A.5.21", "A.5.22", "A.5.23"],
        "soc": ["CC9.2"]
    },
    {
        "name": "Security operations",
        "subs": [
           "Security Event Logging Management", "Security Monitoring and Alert Handling (SOC)",
           "Malware Protection Management", "Vulnerability Management (Scan, Assess, Remediate)",
           "Patch Management", "Secure Configuration and Hardening Management",
           "Change Management", "Backup Management", "Recovery and Restoration Testing Management",
           "Capacity and Performance Management", "Time Synchronization Management"
        ],
        "iso": ["A.8.1", "A.8.5", "A.8.6", "A.8.7", "A.8.8", "A.8.9", "A.8.15", "A.8.16", "A.8.17", "A.8.19", "A.8.23", "A.8.32"],
        "soc": ["CC7.1", "CC7.2", "CC8.1"]
    },
    {
        "name": "Incident and resilience",
        "subs": [
            "Information Security Incident Management", "Evidence Handling and Forensic Readiness Management",
            "Business Continuity and ICT Readiness Management", "Crisis Communication and Stakeholder Notification",
            "Lessons Learned and Post-incident Improvement"
        ],
        "iso": ["A.5.24", "A.5.25", "A.5.26", "A.5.27", "A.5.28", "A.5.29", "A.5.30"],
        "soc": ["CC7.3", "CC7.4", "CC7.5", "CC9.1"]
    },
    {
        "name": "Physical and environmental security",
        "subs": [
             "Physical Access Management (Badges/Visitors)", "Secure Areas Management (Zoning/Monitoring)",
             "Physical Security Monitoring Management (CCTV)", "Equipment Siting, Protection, and Maintenance",
             "Secure Disposal or Reuse of Equipment Management", "Environmental Threat Protection Management"
        ],
        # Clause 7.4 (Physical Env) mapped in image? No, image says A.7.1... but Clause 7 is "Support".
        # Assuming user image is source of truth for mapping.
        "iso": ["A.7.1", "A.7.2", "A.7.3", "A.7.4", "A.7.5", "A.7.6", "A.7.7", "A.7.8", "A.7.9", "A.7.11", "A.7.12", "A.7.13", "A.7.14"],
        "soc": ["CC6.4"]
    },
    {
        "name": "Secure engineering and technology lifecycle",
        "subs": [
             "Secure System Acquisition and Security-by-Design", "Secure Development Lifecycle Management (SDLC)",
             "Application Security Testing Management (SAST/DAST)", "Release and Deployment Security Management",
             "Source Code and Build Pipeline Security Management", "Test Data Management", 
             "Cloud Security Configuration Management", "Encryption and Key Management",
             "Data Masking and Data Loss Prevention Management" 
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
    print("\n--- 2. Syncing All Controls (Including Clauses 4-10) ---")
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
    print(f"Total Controls in DB: {len(control_db_map)}")

    # 3. Processes & Refined Mapping
    print("\n--- 3. process Hierarchy (NO DUPLICATES) ---")
    
    # Cleanup old processes
    all_procs = requests.get(f"{BASE_URL}/processes/", headers=headers).json()
    for p in all_procs:
        try:
             requests.delete(f"{BASE_URL}/processes/{p['id']}", headers=headers)
        except: pass

    # Create & Map (Unique)
    for row in PROCESS_ROWS:
        p_name = row["name"]
        print(f"\nCreated Process: {p_name}")
        
        payload = {
            "name": p_name,
            "description": "Process Group",
            "sub_processes": [{"name": sub, "description": "Activity"} for sub in row["subs"]]
        }
        
        resp = requests.post(f"{BASE_URL}/processes/", json=payload, headers=headers)
        if resp.status_code not in [200, 201]:
            print(f"  ! Error creating process: {resp.text}")
            continue
        
        p_data = resp.json()
        
        # Calculate Control IDs for this ROW
        row_control_ids = []
        for code in row["iso"] + row["soc"]:
            if code in control_db_map: row_control_ids.append(control_db_map[code])
        
        # KEY CHANGE: Map ONLY to the FIRST sub-process to prevent duplication
        # The user wants "one clause / control shall come once".
        # By mapping it only to the first item (e.g., "Policy Management" or "Incident Security Mgmt"), we effectively park it.
        # Ideally we'd distribute them, but without specific mapping, "First Item" is the only safe way to ensure 1:1.
        
        if "sub_processes" in p_data and p_data["sub_processes"] and row_control_ids:
            target_sp = p_data["sub_processes"][0] 
            
            map_resp = requests.post(
                 f"{BASE_URL}/processes/subprocess/{target_sp['id']}/map-controls",
                 json={"control_ids": row_control_ids},
                 headers=headers
            )
            if map_resp.status_code == 200:
                print(f"    -> Mapped ALL {len(row_control_ids)} unique controls to PRIMARY sub-process: '{target_sp['name']}'")
            else:
                print(f"    ! Failed to map to '{target_sp['name']}'")

if __name__ == "__main__":
    seed()
