import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.cloud_resource import CloudResource
from app.utils.encryption import SecurityManager

# --- CONFIGURATION (The "Scrubbing Rules") ---
COMPLIANCE_WHITELIST = {
    "s3_bucket": [
        "is_encrypted",
        "encryption_algorithm",
        "public_access_blocked",
        "versioning_enabled",
        "logging_enabled",
        "mfa_delete"
    ],
    "rds_instance": [
        "storage_encrypted",
        "backup_retention_period",
        "multi_az",
        "iam_database_authentication_enabled",
        "auto_minor_version_upgrade"
    ],
    "ec2_instance": [
        "ebs_optimized",
        "monitoring_state",
        "http_tokens" # IMDSv2
    ]
}

import os

# --- MOCK DATA GENERATOR ---
def fetch_raw_mock_data(provider: str):
    """
    Simulates fetching raw, noisy JSON from a cloud API (e.g., boto3).
    If DEV_MODE=mock, reads from local JSON files in mocks/ directory.
    Otherwise, returns hardcoded internal mock data.
    """
    if os.getenv("DEV_MODE") == "mock":
        print(f"[{provider}] DEV_MODE=mock: Reading from local files...")
        resources = []
        base_path = os.path.join(os.path.dirname(__file__), "../../mocks")
        
        try:
            if provider == "aws":
                # Mock S3 Resource
                s3_path = os.path.join(base_path, "aws_s3_encryption.json")
                if os.path.exists(s3_path):
                    with open(s3_path, "r") as f:
                        s3_data = json.load(f)
                        
                        # DATA NORMALIZATION (Simulating Connector Logic)
                        # Map Raw AWS JSON -> Internal Compliance Format
                        encryption_config = s3_data.get("ServerSideEncryptionConfiguration", {}).get("Rules", [{}])[0].get("ApplyServerSideEncryptionByDefault", {})
                        is_encrypted = "SSEAlgorithm" in encryption_config
                        
                        normalized_data = {
                             # Compliance Fields
                            "is_encrypted": is_encrypted,
                            "encryption_algorithm": encryption_config.get("SSEAlgorithm", "None"),
                            "public_access_blocked": True, # Hardcoded simulation for now or derived from another API call
                            "versioning_enabled": False,
                            
                            # Pass-through of Raw Noisy Data (to prove scrubber removes it)
                            "Owner": s3_data.get("Owner"),
                            "Tags": s3_data.get("Tags")
                        }

                        resources.append({
                            "resource_type": "s3_bucket",
                            "resource_id": "arn:aws:s3:::mock-local-bucket",
                            "raw_data": normalized_data
                        })
            elif provider == "github":
                 # Mock GitHub Resource
                gh_path = os.path.join(base_path, "github_branch_protection.json")
                if os.path.exists(gh_path):
                    with open(gh_path, "r") as f:
                        gh_data = json.load(f)
                        resources.append({
                            "resource_type": "github_repo_rules", # New type needed in whitelist?
                            "resource_id": "github:repo:octocat/Hello-World",
                            "raw_data": gh_data
                        })
        except Exception as e:
            print(f"Error reading mock files: {e}")
            
        return resources

    # Default Internal Mock (as fallback)
    if provider == "aws":
        return [
            {
                "resource_type": "s3_bucket",
                "resource_id": "arn:aws:s3:::finance-data-prod",
                "raw_data": {
                    "Name": "finance-data-prod",
                    "CreationDate": "2023-01-15T10:00:00Z",
                    "Owner": {"DisplayName": "admin", "ID": "12345"}, # NOIICY / PII
                    "is_encrypted": True,
                    "encryption_algorithm": "AES256",
                    "public_access_blocked": True,
                    "versioning_enabled": False, # GAP
                    "Tags": [{"Key": "CostCenter", "Value": "1001"}, {"Key": "Project", "Value": "Apollo"}] # NOISY
                }
            },
            {
                "resource_type": "rds_instance",
                "resource_id": "arn:aws:rds:us-east-1:123:db:main-db",
                "raw_data": {
                    "DBInstanceIdentifier": "main-db",
                    "Engine": "postgres",
                    "storage_encrypted": False, # GAP
                    "backup_retention_period": 7,
                    "multi_az": True,
                    "Endpoint": {"Address": "main-db.cx...", "Port": 5432}, # NOISY
                    "MasterUsername": "root", # SENSITIVE?
                    "iam_database_authentication_enabled": False
                }
            }
        ]
    return []

# --- CORE LOGIC ---
class MetadataScrubberService:
    
    @staticmethod
    def scrub_resource(resource_type: str, raw_data: dict) -> dict:
        """
        Filters raw_data to keep ONLY keys present in COMPLIANCE_WHITELIST.
        """
        whitelist = COMPLIANCE_WHITELIST.get(resource_type, [])
        scrubbed = {}
        
        for key in whitelist:
            if key in raw_data:
                scrubbed[key] = raw_data[key]
        
        return scrubbed

    @staticmethod
    def ingest_resources(tenant_id: str, provider: str, db: Session):
        """
        Orchestrates Fetch -> Scrub -> ENCRYPT -> Save
        """
        print(f"[{tenant_id}] Fetching raw resources from {provider}...")
        raw_resources = fetch_raw_mock_data(provider)
        
        count = 0
        for item in raw_resources:
            r_type = item["resource_type"]
            r_id = item["resource_id"]
            raw = item["raw_data"]
            
            # SCRUB
            cleaned_metadata = MetadataScrubberService.scrub_resource(r_type, raw)
            
            # ENCRYPT
            encrypted_payload = SecurityManager.encrypt_metadata(cleaned_metadata)
            
            # SAVE (Update or Create)
            # Check existing
            existing = db.query(CloudResource).filter(
                CloudResource.resource_id == r_id,
                CloudResource.tenant_id == tenant_id
            ).first()
            
            if existing:
                existing.compliance_metadata = encrypted_payload
                print(f"  -> Updated {r_id} (Encrypted)")
            else:
                new_res = CloudResource(
                    tenant_id=tenant_id,
                    provider=provider,
                    resource_type=r_type,
                    resource_id=r_id,
                    compliance_metadata=encrypted_payload
                )
                db.add(new_res)
                print(f"  -> Created {r_id} (Encrypted)")
            
            count += 1
        
        db.commit()
        return count
