from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.context import ContextIssue, InterestedParty

def seed_context():
    db = SessionLocal()
    print("Seeding Clause 4 Context Registers...")

    # 4.1 Issues
    issues = [
        {"name": "Cloud Provider Dependency", "cat": "External", "pestle": "Technological", "desc": "Reliance on AWS/Azure for core infrastructure.", "impact": "High", "treatment": "Implement Multi-AZ architecture and regular backup testing."},
        {"name": "Regulatory Changes (AI/Privacy)", "cat": "External", "pestle": "Legal", "desc": "Evolving laws around AI and data privacy.", "impact": "Medium", "treatment": "Quarterly legal review and compliance updates."},
        {"name": "Remote Work Security", "cat": "Internal", "pestle": "Social", "desc": "Employees working from uncontrolled networks.", "impact": "High", "treatment": "Enforce MFA, VPN/ZTNA, and Endpoint Protection (MDM)."},
        {"name": "Rapid Hiring/Growth", "cat": "Internal", "pestle": "Organizational", "desc": "Risk of inadequate onboarding or background checks.", "impact": "Medium", "treatment": "Automated HR security workflows and mandatory training."},
    ]
    
    for i in issues:
        exists = db.query(ContextIssue).filter(ContextIssue.name == i["name"]).first()
        if not exists:
            new_issue = ContextIssue(
                name=i["name"],
                category=i["cat"],
                pestle_category=i["pestle"],
                description=i["desc"],
                impact=i["impact"],
                treatment=i["treatment"]
            )
            db.add(new_issue)
            
    # 4.2 Interested Parties
    parties = [
        {"stakeholder": "Customers", "needs": "Data Privacy & Availability", "req": "SOC 2 Type II Report", "map": "A.5.8, A.5.29"},
        {"stakeholder": "Employees", "needs": "Clear Usage Guidelines", "req": "Acceptable Use Policy", "map": "A.5.10"},
        {"stakeholder": "Regulatory Bodies", "needs": "Compliance with Laws", "req": "GDPR / CCPA / HIPAA", "map": "A.5.31, A.5.36"},
        {"stakeholder": "Investors/Board", "needs": "Risk Management", "req": "Quarterly Risk Reports", "map": "Clause 6.1"},
        {"stakeholder": "Cloud Providers (AWS)", "needs": "Adherence to Terms", "req": "Acceptable Usage of Platform", "map": "A.5.22"},
    ]
    
    for p in parties:
        exists = db.query(InterestedParty).filter(InterestedParty.stakeholder == p["stakeholder"]).first()
        if not exists:
            new_p = InterestedParty(
                stakeholder=p["stakeholder"],
                needs=p["needs"],
                requirements=p["req"],
                compliance_mapping=p["map"]
            )
            db.add(new_p)

    db.commit()
    print("Seeded Context Registers.")
    db.close()

if __name__ == "__main__":
    seed_context()
