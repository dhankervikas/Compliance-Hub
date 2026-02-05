
import requests
import sys

# --- CONFIGURATION ---
BASE_URL = "https://assurisk-backend.onrender.com/api/v1"
AUTH_URL = f"{BASE_URL}/auth/login"
USERNAME = "admin"
PASSWORD = "admin123"

# --- SOC 2 & COSO MAPPING DATA (ENRICHED) ---
SOC2_FULL_MAPPING = {
    # --- COSO PRINCIPLE 1: INTEGRITY & ETHICS ---
    "CC1.1": {
        "text": "COSO Principle 1: The entity demonstrates a commitment to integrity and ethical values.",
        "controls": [
            "Code of Conduct acknowledged by employees",
            "Code of Conduct acknowledged by contractors",
            "Confidentiality Agreement acknowledged by employees",
            "Confidentiality Agreement acknowledged by contractors", # Explicitly requested
            "Background checks performed for new hires",
            "Whistleblower Policy (Review & Communication)",
            "Supplier Code of Conduct Review"
        ]
    },
    # --- COSO PRINCIPLE 2: OVERSIGHT ---
    "CC1.2": {
        "text": "COSO Principle 2: The board of directors exercises oversight.",
        "controls": [
            "Board meeting minutes review (Quarterly)",
            "Charter of the Audit Committee",
            "Quarterly security compliance report to Board",
            "independent Director Review of Internal Findings",
            "Board Approval of Information Security Policy"
        ]
    },
    # --- COSO PRINCIPLE 3: STRUCTURES & AUTHORITIES ---
    "CC1.3": {
        "text": "COSO Principle 3: Management establishes structures and authorities.",
        "controls": [
            "Organizational Chart is current",
            "Job Descriptions include security responsibilities",
            "Segregation of Duties (SoD) Matrix Review",
            "Key Personnel Alternate / Succession Plan",
            "Information Security Officer (CISO) Appointment Letter"
        ]
    },
    # --- COSO PRINCIPLE 4: COMPETENCE ---
    "CC1.4": {
        "text": "COSO Principle 4: Attract, develop, and retain competent individuals.",
        "controls": [
            "Performance Reviews (Biannual)",
            "Security Awareness Training (Onboarding)",
            "Security Awareness Training (Annual)",
            "Termination Checklist Log (HR)",
            "Skills Gap Analysis for Security Team"
        ]
    },
    # --- COSO PRINCIPLE 5: ACCOUNTABILITY ---
    "CC1.5": {
        "text": "COSO Principle 5: Accountability for internal control responsibilities.",
        "controls": [
            "Sanction Policy for Security Violations",
            "Contractor Performance Reviews",
            "Employee Disciplinary Action Log",
            "Acknowledgement of Acceptable Use Policy"
        ]
    },

    # --- CC2: INFORMATION & COMMUNICATION ---
    "CC2.1": {
        "text": "COSO Principle 13: Using relevant, quality information.",
        "controls": [
            "Data Classification Policy",
            "Asset Inventory Review (Hardware/Software)",
            "Quality Assurance Checks on Security Reports"
        ]
    },
    "CC2.2": {
        "text": "COSO Principle 14: Internal communication.",
        "controls": [
            "Security Awareness Newsletter / Townhall",
            "Whistleblower Hotline Availability Test",
            "Internal Incident Reporting Channel"
        ]
    },
    "CC2.3": {
        "text": "COSO Principle 15: External communication.",
        "controls": [
            "Customer Data Processing Agreement (DPA)",
            "Privacy Notice on Website",
            "Vendor Security Questionnaire Response Process",
            "Report on Controls (SOC 2 Bridge Letter)"
        ]
    },

    # --- CC3: RISK ASSESSMENT ---
    "CC3.1": {
        "text": "COSO Principle 6: Specifying objectives.",
        "controls": [
            "Business Objectives and Security Goals Doc",
            "Service Level Agreements (SLAs) Definition"
        ]
    },
    "CC3.2": {
        "text": "COSO Principle 7: Risk Identification.",
        "controls": [
            "Annual Risk Assessment Report",
            "Threat Modeling for Key Applications",
            "Vendor Risk Assessment (Third Party)"
        ]
    },
    "CC3.3": {
        "text": "COSO Principle 8: Fraud Risk.",
        "controls": [
            "Fraud Risk Assessment",
            "Expense Report Audits",
            "Anti-Bribery & Corruption Policy Review"
        ]
    },
    "CC3.4": {
        "text": "COSO Principle 9: Assessing Changes.",
        "controls": [
            "Change Management Policy",
            "Quarterly Review of Business Changes",
            "Impact Assessment for Major System Upgrades"
        ]
    },

    # --- CC4: MONITORING ---
    "CC4.1": {
        "text": "COSO Principle 16: Ongoing evaluations.",
        "controls": [
            "Penetration Test Report (Annual)",
            "Vulnerability Scan Schedule (Quarterly)",
            "Internal Audit Plan & Schedule",
            "Daily Log Review Procedure"
        ]
    },
    "CC4.2": {
        "text": "COSO Principle 17: Evaluating deficiencies.",
        "controls": [
            "Corrective Action Plan (CAPA) Log",
            "Root Cause Analysis for Incidents",
            "Security Exceptions Registry"
        ]
    },

    # --- CC5: CONTROL ACTIVITIES ---
    "CC5.1": {
        "text": "COSO Principle 10: Control activities.",
        "controls": [
            "Access Control Policy",
            "Password Policy Configuration",
            "Workstation Security Configuration (MDM)"
        ]
    },
    "CC5.2": {
        "text": "COSO Principle 11: General IT Controls.",
        "controls": [
            "SDLC Policy",
            "Infrastructure as Code (IaC) Review",
            "Encryption Key Management Policy"
        ]
    },
    "CC5.3": {
        "text": "COSO Principle 12: Policies and procedures.",
        "controls": [
            "Policy Management Procedure",
            "Annual Policy Review Log",
            "Document Retention Schedule"
        ]
    },

    # --- SOC 2 SPECIFICS ---
    "CC6.1": {
        "text": "Logical Access: Security software and architecture.",
        "controls": [
            "MFA for Remote Access",
            "MFA for Cloud Infrastructure",
            "Firewall Rules Review (Bi-annual)",
            "WAF Configuration Review",
            "Wireless Security Configuration"
        ]
    },
    "CC6.2": {
        "text": "Logical Access: Authentication.",
        "controls": [
            "User Provisioning Process",
            "Offboarding Access Revocation (Terminated Users)",
            "Quarterly User Access Review",
            "Service Account Inventory"
        ]
    },
    "CC6.3": {
        "text": "Logical Access: Authorization.",
        "controls": [
            "Principle of Least Privilege Review",
            "Role-Based Access Control (RBAC) Matrix",
            "Privileged Access Management (PAM) Review"
        ]
    },
    "CC6.6": { 
        "text": "Physical Access.",
        "controls": [
             "Physical Access Badge logs",
             "Visitor entry logs",
             "CCTV Retention Check",
             "Data Center Access List Review"
        ]
    },
    "CC7.1": {
        "text": "System Operations: Vulnerabilities.",
        "controls": [
            "Patch Management Policy",
            "Antivirus / Endpoint Protection Status",
            "Intrusion Detection System (IDS) Alerts"
        ]
    },
    "CC8.1": {
        "text": "Change Management.",
        "controls": [
            "Production Change Logs",
            "Peer Review of Code Changes",
            "Testing Evidence for Deployments",
            "Emergency Change Procedure",
            "Rollback Plan Verification"
        ]
    },
    # --- AVAILABILITY ---
    "A1.1": {
        "text": "Availability: Capacity Management.",
        "controls": ["Capacity Planning Report", "CPU/Memory Monitoring Alerts", "Bandwidth Utilization Review"]
    },
    "A1.2": {
        "text": "Availability: Backups.",
        "controls": ["Daily Database Backups", "Annual Disaster Recovery Test", "Business Continuity Plan (BCP)", "Backup Restoration Test (Quarterly)"]
    },

    # --- CONFIDENTIALITY ---
    "C1.1": {
        "text": "Confidentiality: Identification.",
        "controls": ["Data Retention & Disposal Policy", "Confidential Data Encryption (At Rest)", "Confidential Data Encryption (In Transit)", "Data Destruction Certificate"]
    },

    # --- PRIVACY ---
    "P1.0": {
        "text": "Privacy: Notice.",
        "controls": ["Privacy Policy Updated", "Cookie Consent Banner", "Privacy Impact Assessment (PIA)"]
    },
    "P2.0": {
        "text": "Privacy: Choice and Consent.",
        "controls": ["Data Minimization Review", "Subject Access Request (SAR) Log", "Opt-out Mechanism Test"]
    }
}

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

def run_seed():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n--- SEEDING ENRICHED SOC 2 (COSO + FULL CRITERIA) ---")
    
    # 1. Find SOC 2 Framework
    resp = requests.get(f"{BASE_URL}/frameworks/", headers=headers)
    frameworks = resp.json()
    soc2 = next((f for f in frameworks if "SOC2" in f["code"]), None)
    
    if not soc2:
        print("Error: SOC 2 Framework not found. Run base seed first.")
        return
        
    fw_id = soc2["id"]
    print(f"Target Framework: {soc2['name']} (ID: {fw_id})")
    
    # 2. Delete Existing SOC 2 Controls (Cleanup)
    print("Fetching existing controls...")
    all_controls = requests.get(f"{BASE_URL}/controls/?limit=5000", headers=headers).json()
    soc_controls = [c for c in all_controls if c["framework_id"] == fw_id]
    print(f"Found {len(soc_controls)} existing controls to replace.")
    
    count_del = 0
    for c in soc_controls:
        try:
            requests.delete(f"{BASE_URL}/controls/{c['id']}", headers=headers)
            count_del += 1
            if count_del % 20 == 0: print(f"Deleted {count_del}...")
        except: pass
    print(f"Deletion complete.")

    # 3. Create New Controls
    print("Creating Enriched Controls...")
    
    # Using 1000 range
    ctrl_counter = 1000 
    for code_prefix, data in SOC2_FULL_MAPPING.items():
        standard_text = data["text"]
        
        for internal_ctrl_title in data["controls"]:
            ctrl_id = f"IC-{ctrl_counter}"
            ctrl_counter += 1
            
            payload = {
                "control_id": ctrl_id, 
                "title": internal_ctrl_title,
                "description": f"Internal control mapped to {code_prefix}. {standard_text}",
                "category": code_prefix,
                "framework_id": fw_id,
                "status": "not_started" 
            }
            
            requests.post(f"{BASE_URL}/controls/", json=payload, headers=headers)
            print(f" -> Created {ctrl_id}: {internal_ctrl_title} ({code_prefix})")

if __name__ == "__main__":
    run_seed()
