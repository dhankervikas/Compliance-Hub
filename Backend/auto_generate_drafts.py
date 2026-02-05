from app.database import SessionLocal
from app.models.policy import Policy
from app.services import ai_service
import datetime
import time

# Robust mappings copied from policies.py to ensure script runs standalone
POLICY_CONTROL_MAP = {
    # 1. Core Governance & ISMS
    "Information Security Policy": "ISO 27001 A.5.1; SOC 2 CC1.1",
    "ISMS Scope Document": "ISO 27001 4.3; SOC 2 Description Criteria",
    "Risk Assessment Methodology": "ISO 27001 6.1.2; SOC 2 CC3.1",
    "Risk Register": "ISO 27001 6.1.3; SOC 2 CC3.2",
    "Risk Treatment Plan": "ISO 27001 6.1.3; SOC 2 CC3.2",
    "Statement of Applicability (SoA)": "ISO 27001 6.1.3",
    "Information Security Objectives": "ISO 27001 6.2",
    "Roles & Responsibilities": "ISO 27001 A.5.2, A.5.4; SOC 2 CC1.2",
    "Management Review Procedure": "ISO 27001 9.3; SOC 2 CC1.3",
    "Internal Audit Procedure": "ISO 27001 9.2; SOC 2 CC4.1",
    "Corrective Action Procedure": "ISO 27001 10.1, 10.2",
    "Document Control Procedure": "ISO 27001 A.5.33; SOC 2 CC1.1",

    # 2. Access Control & Identity
    "Access Control Policy": "ISO 27001 A.5.15-5.18, A.9.x; SOC 2 CC6.1",
    "User Access Management Procedure": "ISO 27001 A.5.16, A.5.18; SOC 2 CC6.2",
    "Privileged Access Management Policy": "ISO 27001 A.8.2; SOC 2 CC6.3",
    "Authentication & Password Policy": "ISO 27001 A.5.17; SOC 2 CC6.1",
    "MFA Policy": "ISO 27001 A.8.5; SOC 2 CC6.1",
    "Access Review Procedure": "ISO 27001 A.5.18, A.9.2.5; SOC 2 CC6.2, CC6.3",

    # 3. Asset & Data Protection
    "Asset Management Policy": "ISO 27001 A.5.9, A.8.1; SOC 2 CC6.1",
    "Asset Inventory": "ISO 27001 A.5.9; SOC 2 CC6.1",
    "Data Classification Policy": "ISO 27001 A.5.12; SOC 2 CC6.1",
    "Data Handling & Labeling Standard": "ISO 27001 A.5.13; SOC 2 CC6.1",
    "Data Retention & Disposal Policy": "ISO 27001 A.8.10, A.7.14; SOC 2 CC3.3",
    "Acceptable Use Policy (AUP)": "ISO 27001 A.5.10; SOC 2 CC1.1",
    "Media Handling & Sanitization Policy": "ISO 27001 A.7.10, A.7.14; SOC 2 CC6.5",
    "Encryption Policy": "ISO 27001 A.8.24; SOC 2 CC6.1, CC6.7",
    "Key Management Procedure": "ISO 27001 A.8.24, A.10; SOC 2 CC6.7",

    # 4. Operations & Technical Security
    "Change Management Policy": "ISO 27001 A.8.32; SOC 2 CC8.1",
    "Secure Configuration Standard": "ISO 27001 A.8.9; SOC 2 CC7.1",
    "Vulnerability Management Policy": "ISO 27001 A.8.8; SOC 2 CC7.1",
    "Patch Management Procedure": "ISO 27001 A.8.8, A.8.19; SOC 2 CC7.1",
    "Malware Protection Policy": "ISO 27001 A.8.7; SOC 2 CC6.8",
    "Backup & Recovery Policy": "ISO 27001 A.8.13; SOC 2 A1.2",
    "Logging & Monitoring Policy": "ISO 27001 A.8.15-8.17; SOC 2 CC7.2",
    "Time Synchronization Standard": "ISO 27001 A.8.18",
    "Network Security Policy": "ISO 27001 A.8.20-8.22; SOC 2 CC6.6",
    "Firewall & Segmentation Standard": "ISO 27001 A.8.22; SOC 2 CC6.6",
    "Cloud Security Policy": "ISO 27001 A.5.23, A.8.1; SOC 2 CC6.1",

    # 5. Incident & Continuity
    "Incident Response Policy": "ISO 27001 A.5.24; SOC 2 CC7.3",
    "Incident Response Plan": "ISO 27001 A.5.24; SOC 2 CC7.4",
    "Breach Notification Procedure": "ISO 27001 A.5.24; SOC 2 CC7.4",
    "Forensic Readiness Procedure": "ISO 27001 A.5.28; SOC 2 CC7.5",
    "Business Continuity Policy": "ISO 27001 A.5.29; SOC 2 A1.2",
    "Business Continuity Plan (BCP)": "ISO 27001 A.5.29; SOC 2 A1.3",
    "Disaster Recovery Plan (DRP)": "ISO 27001 A.8.14 (Redundancy); SOC 2 A1.3",
    "ICT Readiness & Resilience Procedure": "ISO 27001 A.8.14",
    "Crisis Communication Plan": "ISO 27001 A.5.30",

    # 6. Supplier & Third Party
    "Supplier Security Policy": "ISO 27001 A.5.19; SOC 2 CC9.2",
    "Third Party Risk Management Procedure": "ISO 27001 A.5.19-5.22; SOC 2 CC9.2",
    "Supplier Due Diligence Process": "ISO 27001 A.5.21; SOC 2 CC9.2",
    "Contract Security Requirements": "ISO 27001 A.5.20; SOC 2 CC9.2",
    "ICT Supply Chain Security Procedure": "ISO 27001 A.5.23",
    "Vendor Offboarding Procedure": "ISO 27001 A.5.22; SOC 2 CC9.2",

    # 7. Human Resources Security
    "HR Security Policy": "ISO 27001 A.6.1-6.6; SOC 2 CC1.2",
    "Background Screening Procedure": "ISO 27001 A.6.1; SOC 2 CC1.2",
    "Onboarding Security Checklist": "ISO 27001 A.6.2; SOC 2 CC1.2",
    "Offboarding Procedure": "ISO 27001 A.6.5; SOC 2 CC1.2",
    "Security Awareness & Training Policy": "ISO 27001 A.6.3; SOC 2 CC2.2",
    "Disciplinary Process": "ISO 27001 A.6.4; SOC 2 CC1.2",
    "Remote Working Policy": "ISO 27001 A.6.7; SOC 2 CC6.1",

    # 8. Physical & Environmental
    "Physical Security Policy": "ISO 27001 A.7.1-7.14; SOC 2 CC6.4",
    "Facility Access Control Procedure": "ISO 27001 A.7.2; SOC 2 CC6.4",
    "Visitor Management Procedure": "ISO 27001 A.7.2; SOC 2 CC6.4",
    "Secure Area Policy": "ISO 27001 A.7.3; SOC 2 CC6.4",
    "Equipment Protection & Disposal Procedure": "ISO 27001 A.7.14, A.8.1",
    "Environmental Protection Procedure": "ISO 27001 A.7.5, A.7.6",

    # 9. Secure Development
    "Secure SDLC Policy": "ISO 27001 A.8.25; SOC 2 CC3.2",
    "Application Security Standard": "ISO 27001 A.8.26; SOC 2 CC7.1",
    "Secure Coding Guidelines": "ISO 27001 A.8.28; SOC 2 CC7.1",
    "Code Review Procedure": "ISO 27001 A.8.28; SOC 2 CC7.1",
    "Vulnerability Disclosure Policy": "ISO 27001 A.8.8",
    "Release & Deployment Procedure": "ISO 27001 A.8.29",
    "Test Data Management Policy": "ISO 27001 A.8.31",

    # 10. Privacy
    "Privacy Policy": "ISO 27001 A.5.34; SOC 2 Privacy Criteria",
    "Data Subject Rights Procedure": "GDPR / CCPA / privacy regulation",
    "Consent Management Procedure": "GDPR Art 7",
    "Data Processing Inventory": "GDPR Art 30",
    "Cross-Border Transfer Procedure": "GDPR Art 44",

    # 11. Monitoring & Metrics
    "Security Metrics & KPI Procedure": "ISO 27001 9.1",
    "Continuous Monitoring Plan": "ISO 27001 9.1; SOC 2 CC7.2",
    "Control Testing Methodology": "ISO 27001 9.2",
    "Evidence Retention Procedure": "ISO 27001 A.5.33, A.8.10"
}

def auto_generate_all():
    db = SessionLocal()
    
    # 1. Fetch all policies (or just drafts/placeholders)
    # We want to overwrite the 'placeholder' ones we just seeded
    policies = db.query(Policy).filter(Policy.content.contains("**Action Required:**")).all()
    
    print(f"Found {len(policies)} policies pending generation.")
    
    # Context Profile (Mock/Default - in real app fetches from Settings)
    company_profile = {
        "Company Name": "Acme Corp 2026",
        "Policy Owner": "CISO",
        "Policy Approver": "Executive Management"
    }
    
    for i, p in enumerate(policies):
        print(f"[{i+1}/{len(policies)}] Generating content for: {p.name}...")
        
        # Resolve 'Title' / 'Intent'
        control_intent = POLICY_CONTROL_MAP.get(p.name, "ISO 27001:2022 and SOC 2 Standard Compliance")
        
        try:
            # Generate!
            content = ai_service.generate_premium_policy(
                control_title=control_intent,
                policy_name=p.name,
                company_profile=company_profile,
                control_description=p.description or "Compliance Requirement"
            )
            
            # Update DB
            p.content = content
            p.updated_at = datetime.datetime.utcnow()
            db.commit()
            print(f"   -> Success. ({len(content)} chars)")
            
        except Exception as e:
            print(f"   -> FAILED: {e}")
        
        # Slight delay to respect rate limits if any
        # time.sleep(0.5)

    db.close()
    print("Auto-generation complete.")

if __name__ == "__main__":
    auto_generate_all()
