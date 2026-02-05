
import requests
import sys

# --- CONFIGURATION ---
BASE_URL = "https://assurisk-backend.onrender.com/api/v1"
AUTH_URL = f"{BASE_URL}/auth/login"
USERNAME = "admin"
PASSWORD = "admin123"

# --- DATA ---
NEW_FRAMEWORKS = [
    {
        "code": "HIPAA",
        "name": "HIPAA Security Rule",
        "description": "Standards for the protection of electronic protected health information (ePHI)."
    },
    {
        "code": "PCI_DSS_v4",
        "name": "PCI DSS v4.0",
        "description": "Payment Card Industry Data Security Standard for securing cardholder data."
    },
    {
        "code": "ISO_27701",
        "name": "ISO/IEC 27701:2019",
        "description": "Privacy Information Management System (PIMS) extension to ISO 27001."
    },
    {
        "code": "ISO_42001",
        "name": "ISO/IEC 42001:2023",
        "description": "Artificial Intelligence Management System (AIMS)."
    },
    {
        "code": "GDPR",
        "name": "GDPR",
        "description": "General Data Protection Regulation for data protection and privacy in the EU."
    },
    {
        "code": "US_DATA_PRIVACY",
        "name": "US Data Privacy",
        "description": "Comprehensive framework covering CCPA, CPRA, and state-level privacy laws."
    },
    {
        "code": "NIST_800_53",
        "name": "NIST SP 800-53 r5",
        "description": "Security and Privacy Controls for Information Systems and Organizations."
    },
    {
        "code": "NIST_CSF_2",
        "name": "NIST CSF 2.0",
        "description": "The NIST Cybersecurity Framework Version 2.0 (Govern, Identify, Protect, Detect, Respond, Recover)."
    }
]

# Sample controls to make them look "alive"
SAMPLE_CONTROLS = {
    "HIPAA": [
        "Access Control: Unique User Identification", 
        "Audit Controls: Review Records of Activity",
        "Person or Entity Authentication"
    ],
    "PCI_DSS_v4": [
        "Install and Maintain Network Security Controls",
        "Protect Stored Account Data",
        "Encrypt Cardholder Data Across Open/Public Networks"
    ],
    "ISO_27701": [
        "Conditions for collection and processing",
        "Obligations to PII principals",
        "Privacy by design and privacy by default"
    ],
    "ISO_42001": [
        "AI Risk Assessment",
        "AI System Impact Assessment",
        "Data Quality and Management for AI"
    ],
    "GDPR": [
        "Lawfulness of processing",
        "Right to erasure ('right to be forgotten')",
        "Data protection impact assessment"
    ],
    "US_DATA_PRIVACY": [
        "Consumer Right to Know",
        "Consumer Right to Delete",
        "Do Not Sell My Personal Information"
    ],
    "NIST_800_53": [
        "AC-1 Access Control Policy and Procedures",
        "AU-2 Audit Events",
        "IR-4 Incident Handling"
    ],
    "NIST_CSF_2": [
        "GV.OC-01: Organizational Context",
        "ID.AM-01: Inventories of Hardware Managed",
        "PR.AA-01: Identity Management and Authentication"
    ]
}

# --- PROCESS CACHE ---
# We need to map controls to sub-processes. Let's fetch them first.
processes_cache = []

def get_token():
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

def fetch_processes(headers):
    global processes_cache
    print("Fetching existing processes for mapping...")
    resp = requests.get(f"{BASE_URL}/processes/", headers=headers)
    if resp.status_code == 200:
        processes_cache = resp.json()
        print(f"Loaded {len(processes_cache)} processes.")
    else:
        print("Failed to load processes.")

def get_target_subprocess(control_text):
    # Simple logic to pick a relevant sub-process based on keywords
    text = control_text.lower()
    
    # 1. Flatten all sub-processes
    all_subs = []
    for p in processes_cache:
        all_subs.extend(p.get("sub_processes", []))
    
    # 2. Keyword Match
    for sub in all_subs:
        s_name = sub["name"].lower()
        if "access" in text and "access" in s_name: return sub["id"]
        if "risk" in text and "risk" in s_name: return sub["id"]
        if "incident" in text and "incident" in s_name: return sub["id"]
        if "data" in text and "asset" in s_name: return sub["id"]
        if "policy" in text and "governance" in s_name: return sub["id"]
        if "privacy" in text and "compliance" in s_name: return sub["id"]
        if "ai" in text and "development" in s_name: return sub["id"]

    # 3. Fallback: Return first available or hardcoded ID
    if all_subs: return all_subs[0]["id"]
    return 1 # Fallback ID

def run_seed():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    fetch_processes(headers)

    print("\n--- SEEDING EXTENDED FRAMEWORKS ---")
    
    for fw_def in NEW_FRAMEWORKS:
        print(f"Creating Framework: {fw_def['code']}...")
        
        # 1. Create Framework
        resp = requests.post(f"{BASE_URL}/frameworks/", json=fw_def, headers=headers)
        if resp.status_code == 201:
            fw_data = resp.json()
            fw_id = fw_data["id"]
            print(f" -> Created ID: {fw_id}")
            
            # 2. Create Sample Controls
            controls = SAMPLE_CONTROLS.get(fw_def["code"], [])
            for c_text in controls:
                target_sub_id = get_target_subprocess(c_text)
                
                payload = {
                    "code": c_text[:10].upper().replace(" ", "-"), # Fake short code
                    "title": c_text,
                    "description": f"Standard control requirement for {fw_def['name']}.",
                    "framework_id": fw_id,
                    "sub_process_id": target_sub_id,
                    "status": "not_started" 
                }
                
                c_resp = requests.post(f"{BASE_URL}/controls/", json=payload, headers=headers)
                if c_resp.status_code == 201:
                    print(f"    -> Added Control: {c_text}")
                else:
                    print(f"    -> Failed Control: {c_resp.text}")

        elif resp.status_code == 400 and "already exists" in resp.text:
             print(" -> Already exists, skipping.")
        else:
            print(f" -> Failed: {resp.text}")

if __name__ == "__main__":
    run_seed()
