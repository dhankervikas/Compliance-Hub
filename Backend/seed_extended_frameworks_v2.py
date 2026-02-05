
import requests
import sys

# --- CONFIGURATION ---
BASE_URL = "http://localhost:8000/api/v1"
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

# --- CACHES ---
processes_cache = []
existing_frameworks = {}

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

def fetch_frameworks(headers):
    global existing_frameworks
    print("Fetching existing frameworks...")
    resp = requests.get(f"{BASE_URL}/frameworks/", headers=headers)
    if resp.status_code == 200:
        fws = resp.json()
        for f in fws:
            existing_frameworks[f["code"]] = f["id"]
        print(f"Loaded {len(existing_frameworks)} existing frameworks.")

def get_target_subprocess(control_text):
    text = control_text.lower()
    all_subs = []
    for p in processes_cache:
        all_subs.extend(p.get("sub_processes", []))
    
    for sub in all_subs:
        s_name = sub["name"].lower()
        if "access" in text and "access" in s_name: return sub["id"]
        if "risk" in text and "risk" in s_name: return sub["id"]
        if "incident" in text and "incident" in s_name: return sub["id"]
        if "data" in text and "asset" in s_name: return sub["id"]
        if "policy" in text and "governance" in s_name: return sub["id"]
        if "privacy" in text and "compliance" in s_name: return sub["id"]
        if "ai" in text and "development" in s_name: return sub["id"]

    if all_subs: return all_subs[0]["id"]
    return 1

def run_seed():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    fetch_processes(headers)
    fetch_frameworks(headers)

    print("\n--- SEEDING EXTENDED FRAMEWORKS ---")
    
    for fw_def in NEW_FRAMEWORKS:
        fw_code = fw_def["code"]
        print(f"Processing Framework: {fw_code}...")
        
        fw_id = None
        
        # 1. Check if exists or Create
        if fw_code in existing_frameworks:
            fw_id = existing_frameworks[fw_code]
            print(f" -> Found Existing ID: {fw_id}")
        else:
            resp = requests.post(f"{BASE_URL}/frameworks/", json=fw_def, headers=headers)
            if resp.status_code == 201:
                fw_data = resp.json()
                fw_id = fw_data["id"]
                print(f" -> Created ID: {fw_id}")
            else:
                print(f" -> Creation Failed: {resp.text}")
                continue

        # 2. Create Sample Controls
        controls = SAMPLE_CONTROLS.get(fw_code, [])
        for c_text in controls:
            target_sub_id = get_target_subprocess(c_text)
            
            # FIXED: control_id field name (was 'code')
            short_id = c_text[:10].upper().replace(" ", "-").replace(":", "")
            
            payload = {
                "control_id": short_id,   # CHANGED FROM code -> control_id
                "title": c_text,
                "description": f"Standard control requirement for {fw_def['name']}.",
                "framework_id": fw_id,
                "sub_process_id": target_sub_id, # Can be null in model? Let's assume passed.
                "status": "not_started" 
            }
            # Note: app/schemas/control.py: ControlCreate doesn't list sub_process_id? 
            # Wait, let's double check if sub_process_id is in ControlCreate.
            # The schema I read earlier: 
            # class ControlCreate(ControlBase):
            #     framework_id: int
            #     owner: Optional[str] = None
            #     status: ControlStatus = ControlStatus.NOT_STARTED
            # It DOES NOT seem to have sub_process_id explicitly??
            # But the 'Control' model likely has it.
            # If the API doesn't accept it, my smart distribution logic via API might fail unless the API was updated 
            # or it uses **kwargs. I should check if my previous smart seed accessed DB directly or API.
            # Previous seed used direct DB access (Session).
            # This script uses API.
            # I'll try sending it. If rejected, I might need a 'patch' endpoint or direct DB seed.
            # But for Dashboard viewing, we just need the control to exist.
            
            c_resp = requests.post(f"{BASE_URL}/controls/", json=payload, headers=headers)
            if c_resp.status_code == 201:
                print(f"    -> Added Control: {short_id}")
            else:
                # If 422, maybe sub_process_id is not allowed?
                print(f"    -> Failed Control {short_id}: {c_resp.text}")

if __name__ == "__main__":
    run_seed()
