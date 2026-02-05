
import boto3
import requests
import json
import os
import random
from datetime import datetime, timedelta

# CONFIG
SCAN_DIR = "data/scans"
BASE_URL = "http://localhost:8000/api/v1"
# MOCK CREDENTIALS (for demonstration context)
AWS_REGION = "us-east-1"
GITHUB_REPO = "dhankervikas/assurisk-backend"

class InfrastructurePoller:
    def __init__(self):
        self.findings = []
        os.makedirs(SCAN_DIR, exist_ok=True)
        
    def scan_aws(self):
        print("--- Scanning AWS Infrastructure ---")
        # Simulating Boto3 calls
        # client = boto3.client("iam")
        # users = client.list_users() ...
        
        # MOCK FINDINGS mapped to ISO 27001
        
        # A.8.5 Secure Authentication (MFA)
        mfa_enabled = random.choice([True, False])
        self.findings.append({
            "control_id": "A.8.5",
            "source": "AWS IAM",
            "check": "Root MFA Enabled",
            "status": "PASS" if mfa_enabled else "FAIL",
            "severity": "CRITICAL",
            "details": "Root account has MFA enabled." if mfa_enabled else "Root account missing MFA.",
            "timestamp": datetime.now().isoformat()
        })
        
        # A.8.12 Data Leakage Prevention (S3 Public Access)
        s3_secure = True
        self.findings.append({
            "control_id": "A.8.12",
            "source": "AWS S3",
            "check": "S3 Public Access Block",
            "status": "PASS",
            "severity": "HIGH",
            "details": "All S3 buckets have Public Access Block enabled.",
            "timestamp": datetime.now().isoformat()
        })
        
    def scan_github(self):
        print("--- Scanning GitHub Repository ---")
        # Simulating GitHub API calls
        
        # A.8.25 Secure Development Lifecycle (Branch Protection)
        branch_protected = True
        self.findings.append({
            "control_id": "A.8.25",
            "source": "GitHub",
            "check": "Branch Protection (Main)",
            "status": "PASS" if branch_protected else "FAIL",
            "details": f"Main branch protection active on {GITHUB_REPO}",
            "timestamp": datetime.now().isoformat()
        })
        
        # A.8.4 Access to Source Code (Dependabot)
        dependabot_active = random.choice([True, False])
        self.findings.append({
            "control_id": "A.8.4",
            "source": "GitHub",
            "check": "Dependabot Alerts",
            "status": "PASS" if dependabot_active else "WARN",
            "details": "Dependabot active." if dependabot_active else "Dependabot not configured.",
            "timestamp": datetime.now().isoformat()
        })

    def generate_artifact(self):
        filename = f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(SCAN_DIR, filename)
        
        report = {
            "scan_id": filename.replace("scan_", "").replace(".json", ""),
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": len(self.findings),
                "pass": len([f for f in self.findings if f["status"] == "PASS"]),
                "fail": len([f for f in self.findings if f["status"] == "FAIL"])
            },
            "findings": self.findings
        }
        
        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)
            
        print(f"[ARTIFACT] Generated {filepath}")
        return report

    def push_to_backend(self):
        # Optional: Push status to API to update "Last Automated Check"
        print("Syncing with Backend API...")
        # (Simplified: In a real app we'd authenticate and PATCH the controls)
        pass

if __name__ == "__main__":
    poller = InfrastructurePoller()
    poller.scan_aws()
    poller.scan_github()
    report = poller.generate_artifact()
    
    # Simple CLI Output
    print(f"\nScan Complete: {report['summary']['pass']} Passing, {report['summary']['fail']} Failing")
