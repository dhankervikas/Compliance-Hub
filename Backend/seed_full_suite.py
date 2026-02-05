from app.database import SessionLocal
from app.models.policy import Policy
import datetime

def seed_comprehensive_suite():
    db = SessionLocal()
    
    # Full list provided by user (grouped for clarity but flattened here)
    policy_names = [
        # 1. Governance
        "Information Security Policy", "ISMS Scope Document", "Risk Assessment Methodology", "Risk Register",
        "Risk Treatment Plan", "Statement of Applicability (SoA)", "Information Security Objectives",
        "Roles & Responsibilities", "Management Review Procedure", "Internal Audit Procedure",
        "Corrective Action Procedure", "Document Control Procedure",
        
        # 2. Access
        "Access Control Policy", "User Access Management Procedure", "Privileged Access Management Policy",
        "Authentication & Password Policy", "MFA Policy", "Access Review Procedure",
        
        # 3. Asset
        "Asset Management Policy", "Asset Inventory", "Data Classification Policy", "Data Handling & Labeling Standard",
        "Data Retention & Disposal Policy", "Acceptable Use Policy (AUP)", "Media Handling & Sanitization Policy",
        "Encryption Policy", "Key Management Procedure",
        
        # 4. Ops
        "Change Management Policy", "Secure Configuration Standard", "Vulnerability Management Policy",
        "Patch Management Procedure", "Malware Protection Policy", "Backup & Recovery Policy",
        "Logging & Monitoring Policy", "Time Synchronization Standard", "Network Security Policy",
        "Firewall & Segmentation Standard", "Cloud Security Policy",
        
        # 5. Incident
        "Incident Response Policy", "Incident Response Plan", "Breach Notification Procedure",
        "Forensic Readiness Procedure", "Business Continuity Policy", "Business Continuity Plan (BCP)",
        "Disaster Recovery Plan (DRP)", "ICT Readiness & Resilience Procedure", "Crisis Communication Plan",
        
        # 6. Supplier
        "Supplier Security Policy", "Third Party Risk Management Procedure", "Supplier Due Diligence Process",
        "Contract Security Requirements", "ICT Supply Chain Security Procedure", "Vendor Offboarding Procedure",
        
        # 7. HR
        "HR Security Policy", "Background Screening Procedure", "Onboarding Security Checklist",
        "Offboarding Procedure", "Security Awareness & Training Policy", "Disciplinary Process",
        "Remote Working Policy",
        
        # 8. Physical
        "Physical Security Policy", "Facility Access Control Procedure", "Visitor Management Procedure",
        "Secure Area Policy", "Equipment Protection & Disposal Procedure", "Environmental Protection Procedure",
        
        # 9. Secure Dev
        "Secure SDLC Policy", "Application Security Standard", "Secure Coding Guidelines", "Code Review Procedure",
        "Vulnerability Disclosure Policy", "Release & Deployment Procedure", "Test Data Management Policy",
        
        # 10. Privacy
        "Privacy Policy", "Data Subject Rights Procedure", "Consent Management Procedure",
        "Data Processing Inventory", "Cross-Border Transfer Procedure",
        
        # 11. Monitoring
        "Security Metrics & KPI Procedure", "Continuous Monitoring Plan", "Control Testing Methodology",
        "Evidence Retention Procedure"
    ]
    
    print(f"Checking {len(policy_names)} policies...")
    
    created_count = 0
    for name in policy_names:
        exists = db.query(Policy).filter(Policy.name == name).first()
        if not exists:
            # Determine Owner based on name (simple heuristics)
            owner = "CISO"
            if "HR" in name or "Human" in name: owner = "Head of HR"
            elif "Legal" in name or "Contract" in name or "Privacy" in name: owner = "Legal Counsel"
            elif "Development" in name or "Code" in name or "SDLC" in name: owner = "Head of Engineering"
            elif "Operations" in name or "Patch" in name or "Network" in name: owner = "IT Director"
            
            # Helper content (Prompting user to generate)
            placeholder_content = f"# {name}\n\n*This document is ready for generation.*\n\n**Action Required:**\nClick the 'Generate Draft' button to create the content for this policy based on the defined ISO 27001 / SOC 2 controls."
            
            policy = Policy(
                name=name,
                description=f"Official {name} for compliance requirements.",
                content=placeholder_content,
                status="Draft",
                owner=owner,
                version="0.1",
                updated_at=datetime.datetime.utcnow()
            )
            db.add(policy)
            created_count += 1
            print(f" [CREATED] {name}")
        else:
            print(f" [EXISTS]  {name}")
            
    db.commit()
    db.close()
    print(f"\nSeeding Complete. Added {created_count} new policies.")

if __name__ == "__main__":
    seed_comprehensive_suite()
