import os
import sys

# Ensure app is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.services.metadata_scrubber import MetadataScrubberService
from app.services.compliance_evaluator import ComplianceEvaluator
from app.models.control import Control
from app.models.framework import Framework
from app.utils.encryption import SecurityManager

def seed_data():
    db = SessionLocal()
    tenant_id = "default_tenant" # Using default for now to be visible to admin
    
    print("--- Seeding Mock Compliance Data ---")
    
    # 1. Ensure Encryption Key is Loaded (handled by config import in services)
    
    # 2. Ingest Mock Cloud Resources (Pass & Fail scenarios)
    # We'll bypass the raw fetcher to insert specific scenarios manually for control over Pass/Fail ratio
    
    scenarios = [
        {
            "provider": "aws", "type": "s3_bucket", "id": "arn:aws:s3:::secure-bucket",
            "data": {"is_encrypted": True, "public_access_blocked": True}
        },
        {
            "provider": "aws", "type": "s3_bucket", "id": "arn:aws:s3:::leaky-bucket",
            "data": {"is_encrypted": False, "public_access_blocked": False}
        },
         {
            "provider": "aws", "type": "rds_instance", "id": "arn:aws:rds:db-prod",
            "data": {"storage_encrypted": True, "multi_az": True}
        },
        {
            "provider": "aws", "type": "rds_instance", "id": "arn:aws:rds:db-dev",
            "data": {"storage_encrypted": False, "multi_az": False}
        },
        {
            "provider": "github", "type": "github_repo_rules", "id": "github:repo:assurisk/backend",
            "data": {"required_pull_request_reviews": {"required_approving_review_count": 2}}
        }
    ]
    
    print(f"Creating {len(scenarios)} mock resources...")
    from app.models.cloud_resource import CloudResource
    
    for scen in scenarios:
        # Manually encrypt and save to avoid relying on the internal mock fetcher for these specific scenarios
        encrypted = SecurityManager.encrypt_metadata(scen["data"])
        
        # Upsert Resource
        existing = db.query(CloudResource).filter_by(resource_id=scen["id"]).first()
        if existing:
            existing.compliance_metadata = encrypted
        else:
            new_res = CloudResource(
                tenant_id=tenant_id,
                provider=scen["provider"],
                resource_type=scen["type"],
                resource_id=scen["id"],
                compliance_metadata=encrypted
            )
            db.add(new_res)
    db.commit()
    
    # 3. Ensure Controls Exist for Mapping (Governance, Risk, Technical)
    # The Evaluator maps to: A.10.1, A.6.1, A.12.1, A.8.1
    # We need to make sure these exist in the controls table with the correct 'domain'
    
    controls_to_ensure = [
        {"id": "A.10.1", "title": "Cryptography", "domain": "Technical Security"},
        {"id": "A.6.1", "title": "Access Control", "domain": "Governance"},
        {"id": "A.12.1", "title": "Operational Resilience", "domain": "Risk Management"},
        {"id": "A.8.1", "title": "Configuration Management", "domain": "Technical Security"},
    ]
    
    # Get or Create Dummy Framework
    fw = db.query(Framework).filter_by(code="ISO42001_MOCK").first()
    if not fw:
        fw = Framework(code="ISO42001_MOCK", name="ISO 42001 (Mock)", description="Mock framework", tenant_id=tenant_id)
        db.add(fw)
        db.commit()
    
    for c_data in controls_to_ensure:
        c = db.query(Control).filter_by(control_id=c_data["id"]).first()
        if not c:
            c = Control(
                control_id=c_data["id"],
                title=c_data["title"],
                domain=c_data["domain"],
                framework_id=fw.id,
                tenant_id=tenant_id
            )
            db.add(c)
        else:
            # Update domain if missing (important for dashboard)
            c.domain = c_data["domain"]
            db.add(c)
            
    db.commit()
    
    # 4. Run Evaluator
    ComplianceEvaluator.run_evaluation_for_tenant(db, tenant_id)
    print("Done.")

if __name__ == "__main__":
    seed_data()
