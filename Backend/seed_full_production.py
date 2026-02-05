
import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"
AUTH_URL = f"{BASE_URL}/auth/login"

USERNAME = "admin"
PASSWORD = "admin123"

# --- DATASETS ---

FRAMEWORKS = [
    {
        "name": "SOC 2 - Trust Services Criteria (2017)",
        "code": "SOC2_2017",
        "description": "AICPA Trust Services Criteria for Security, Availability, Processing Integrity, Confidentiality, and Privacy",
        "version": "2017"
    },
    {
        "name": "ISO/IEC 27001:2022",
        "code": "ISO27001_2022",
        "description": "Information security, cybersecurity and privacy protection — Information security management systems — Requirements",
        "version": "2022"
    }
]

# (Simplified list for demo scalability, but significantly expanded from before)
CONTROLS_SOC2 = [
    # Common Criteria (Security)
    {"id": "CC1.1", "title": "Tone at the Top", "cat": "Security"},
    {"id": "CC1.2", "title": "Board Oversight", "cat": "Security"},
    {"id": "CC2.1", "title": "Internal Communication", "cat": "Security"},
    {"id": "CC3.1", "title": "Risk Mitigation", "cat": "Security"},
    {"id": "CC4.1", "title": "Evaluation of Controls", "cat": "Security"},
    {"id": "CC5.1", "title": "Deficiency Evaluation", "cat": "Security"},
    {"id": "CC6.1", "title": "Logical Access Security", "cat": "Security"},
    {"id": "CC6.2", "title": "User Provisioning", "cat": "Security"},
    {"id": "CC6.3", "title": "Least Privilege Access", "cat": "Security"},
    {"id": "CC7.1", "title": "System Monitoring", "cat": "Security"},
    {"id": "CC8.1", "title": "Change Management", "cat": "Security"},
    
    # Availability
    {"id": "A1.1", "title": "Capacity Management", "cat": "Availability"},
    {"id": "A1.2", "title": "Environmental Protections", "cat": "Availability"},
    {"id": "A1.3", "title": "Data Backup & Recovery", "cat": "Availability"},

    # Confidentiality
    {"id": "C1.1", "title": "Confidentiality of Information", "cat": "Confidentiality"},
    {"id": "C1.2", "title": "Disposal of Confidential Info", "cat": "Confidentiality"},

    # Privacy
    {"id": "P1.0", "title": "Privacy Notice", "cat": "Privacy"},
    {"id": "P2.1", "title": "Choice and Consent", "cat": "Privacy"},
    {"id": "P3.1", "title": "Collection Limitation", "cat": "Privacy"},
    {"id": "P5.0", "title": "Access to Personal Info", "cat": "Privacy"},
]

CONTROLS_ISO = [
    # A.5 Organizational
    {"id": "A.5.1", "title": "Policies for information security", "cat": "Organizational"},
    {"id": "A.5.2", "title": "Information security roles and responsibilities", "cat": "Organizational"},
    {"id": "A.5.3", "title": "Segregation of duties", "cat": "Organizational"},
    {"id": "A.5.4", "title": "Management responsibilities", "cat": "Organizational"},
    {"id": "A.5.24", "title": "Information security incident management planning", "cat": "Organizational"},

    # A.6 People
    {"id": "A.6.1", "title": "Screening", "cat": "People"},
    {"id": "A.6.2", "title": "Terms and conditions of employment", "cat": "People"},
    {"id": "A.6.3", "title": "Information security awareness, education and training", "cat": "People"},
    {"id": "A.6.4", "title": "Disciplinary process", "cat": "People"},

    # A.7 Physical
    {"id": "A.7.1", "title": "Physical security perimeters", "cat": "Physical"},
    {"id": "A.7.2", "title": "Physical entry", "cat": "Physical"},
    {"id": "A.7.3", "title": "Securing offices, rooms and facilities", "cat": "Physical"},

    # A.8 Technological
    {"id": "A.8.1", "title": "User endpoint devices", "cat": "Technological"},
    {"id": "A.8.2", "title": "Privileged access rights", "cat": "Technological"},
    {"id": "A.8.3", "title": "Information access restriction", "cat": "Technological"},
    {"id": "A.8.4", "title": "Access to source code", "cat": "Technological"},
    {"id": "A.8.9", "title": "Configuration management", "cat": "Technological"},
    {"id": "A.8.10", "title": "Information deletion", "cat": "Technological"},
    {"id": "A.8.24", "title": "Use of cryptography", "cat": "Technological"},
]

PROCESS_HIERARCHY = [
    {
        "name": "Human Resources",
        "description": "Personnel security and management lifecycle.",
        "sub_processes": [
            {
                "name": "Hiring & Onboarding",
                "description": "Screening and setting initial access.",
                "controls": ["CC6.2", "A.6.1", "A.6.2"]
            },
            {
                "name": "Training & Awareness",
                "description": "Continuous security education.",
                "controls": ["CC2.1", "A.6.3"]
            },
            {
                "name": "Offboarding",
                "description": "Termination procedures and access revocation.",
                "controls": ["CC6.1", "A.6.4"]
            }
        ]
    },
    {
        "name": "Corporate Governance",
        "description": "Strategic direction and oversight.",
        "sub_processes": [
            {
                "name": "Policy Management",
                "description": "Establishing and reviewing policies.",
                "controls": ["CC1.1", "CC1.2", "A.5.1", "A.5.4"]
            },
            {
                "name": "Risk Management",
                "description": "Identifying and treating risks.",
                "controls": ["CC3.1", "CC5.1"]
            },
            {
                "name": "Roles & Responsibilities",
                "description": "Defining security organization.",
                "controls": ["A.5.2", "A.5.3"]
            }
        ]
    },
    {
        "name": "IT Operations",
        "description": "Management of IT infrastructure and services.",
        "sub_processes": [
            {
                "name": "Change Management",
                "description": "Controlling changes to systems.",
                "controls": ["CC8.1", "A.8.9"]
            },
            {
                "name": "Backups & Recovery",
                "description": "Ensuring data availability.",
                "controls": ["A1.3", "A1.1"]
            },
            {
                "name": "Encryption",
                "description": "Protecting data at rest and transit.",
                "controls": ["C1.1", "A.8.24"]
            }
        ]
    },
    {
        "name": "Access Management",
        "description": "Controlling logical access to systems.",
        "sub_processes": [
            {
                "name": "Access Provisioning",
                "description": "Granting and reviewing access.",
                "controls": ["CC6.1", "CC6.3", "A.8.2", "A.8.3"]
            },
            {
                "name": "Device Security",
                "description": "Securing workstations and mobile devices.",
                "controls": ["A.8.1"]
            }
        ]
    },
    {
        "name": "Physical Security",
        "description": "Protection of physical assets.",
        "sub_processes": [
            {
                "name": "Facility Access",
                "description": "Controlling entry to offices.",
                "controls": ["A1.2", "A.7.1", "A.7.2", "A.7.3"]
            }
        ]
    },
    {
        "name": "Privacy",
        "description": "Management of personal data.",
        "sub_processes": [
            {
                "name": "Data Subject Rights",
                "description": "Handling consent and access requests.",
                "controls": ["P1.0", "P2.1", "P5.0"]
            },
            {
                "name": "Data Lifecycle",
                "description": "Collection and disposal.",
                "controls": ["P3.1", "C1.2", "A.8.10"]
            }
        ]
    },
    {
        "name": "Incident Management",
        "description": "Responding to security events.",
        "sub_processes": [
            {
                "name": "Incident Response",
                "description": "Detection and reaction.",
                "controls": ["CC7.1", "A.5.24"]
            }
        ]
    }
]

# --- SCRIPT LOGIC ---

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
    print("\n--- Seeding Frameworks ---")
    fw_map = {} # Code -> ID
    for fw in FRAMEWORKS:
        resp = requests.post(f"{BASE_URL}/frameworks/", json=fw, headers=headers)
        if resp.status_code in [200, 201]:
             fw_data = resp.json()
             fw_map[fw["code"]] = fw_data["id"]
             print(f"[OK] Framework: {fw['code']}")
        elif resp.status_code == 409 or "already exists" in resp.text:
             # Fetch ID if exists
             all_fw = requests.get(f"{BASE_URL}/frameworks/", headers=headers).json()
             existing = next(f for f in all_fw if f["code"] == fw["code"])
             fw_map[fw["code"]] = existing["id"]
             print(f"[SKIP] Framework {fw['code']} exists.")
        else:
            print(f"[FAIL] Framework {fw['code']}: {resp.text}")

    # 2. Controls
    print("\n--- Seeding Controls ---")
    control_db_map = {} # Control Code -> DB ID

    def seed_controls(ctrl_list, fw_code):
        if fw_code not in fw_map:
            print(f"[SKIP] missing framework id for {fw_code}")
            return
        fw_id = fw_map[fw_code]
        for c in ctrl_list:
            c_payload = {
                "control_id": c["id"],
                "title": c["title"],
                "description": f"Standard control for {c['cat']}",
                "category": c["cat"],
                "priority": "high",
                "framework_id": fw_id
            }
            # Try create
            resp = requests.post(f"{BASE_URL}/controls/", json=c_payload, headers=headers)
            if resp.status_code in [200, 201]:
                cd = resp.json()
                control_db_map[c["id"]] = cd["id"]
                # print(f"  + {c['id']}")
            elif "already exists" in resp.text or resp.status_code == 409:
                # Need to fetch ID for mapping
                # Assuming not efficient but simple: fetch all controls for frameowrk
                pass # Will do bulk fetch after
            else:
                 print(f"  ! Failed {c['id']}: {resp.text}")

    seed_controls(CONTROLS_SOC2, "SOC2_2017")
    seed_controls(CONTROLS_ISO, "ISO27001_2022")
    
    # Refresh Control Map (bulk fetch)
    print("Refining Control Map...")
    all_c = requests.get(f"{BASE_URL}/controls/?limit=1000", headers=headers).json()
    for c in all_c:
        control_db_map[c["control_id"]] = c["id"]
    print(f"Total Controls in DB: {len(control_db_map)}")

    # 3. Processes & Mappings
    print("\n--- Seeding Process Hierarchy ---")
    
    # Get existing processes to avoid dups or delete them?
    # Strategy: Wipe existing processes via the new DELETE API to ensure clean slate
    all_procs = requests.get(f"{BASE_URL}/processes/", headers=headers).json()
    for p in all_procs:
        requests.delete(f"{BASE_URL}/processes/{p['id']}", headers=headers)
        print(f"  - Cleaned up old process: {p['name']}")

    for proc_def in PROCESS_HIERARCHY:
        print(f"Creating: {proc_def['name']}")
        
        # Build payload
        payload = {
            "name": proc_def["name"],
            "description": proc_def["description"],
            "sub_processes": [
                {"name": sp["name"], "description": sp["description"]}
                for sp in proc_def["sub_processes"]
            ]
        }
        
        resp = requests.post(f"{BASE_URL}/processes/", json=payload, headers=headers)
        if resp.status_code not in [200, 201]:
            print(f"  ! Failed: {resp.text}")
            continue
            
        p_data = resp.json()
        
        # Map Controls
        if "sub_processes" in p_data:
            for sp_created in p_data["sub_processes"]:
                # specific subprocess definition from our list
                sp_orig = next(s for s in proc_def["sub_processes"] if s["name"] == sp_created["name"])
                
                c_ids_to_map = []
                for c_code in sp_orig.get("controls", []):
                    if c_code in control_db_map:
                        c_ids_to_map.append(control_db_map[c_code])
                    else:
                        print(f"    ! Warning: Control {c_code} not found in DB.")
                
                if c_ids_to_map:
                    map_resp = requests.post(
                         f"{BASE_URL}/processes/subprocess/{sp_created['id']}/map-controls",
                         json={"control_ids": c_ids_to_map},
                         headers=headers
                    )
                    if map_resp.status_code == 200:
                        print(f"    -> {sp_created['name']}: Mapped {len(c_ids_to_map)} controls.")

if __name__ == "__main__":
    seed()
