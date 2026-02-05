import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.services.metadata_scrubber import MetadataScrubberService
from app.models.cloud_resource import CloudResource

# Setup DB
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def retrieve_and_show(tenant_id="default_tenant"):
    db = SessionLocal()
    
    print(f"\n--- Running Metadata Scrubber for {tenant_id} ---")
    
    # 1. Run Ingestion (Mock AWS)
    count = MetadataScrubberService.ingest_resources(tenant_id, "aws", db)
    print(f"Ingested {count} resources.")
    
    # 2. Verify Data in DB
    print("\n--- Verifying Stored Data ---")
    resources = db.query(CloudResource).filter(CloudResource.tenant_id == tenant_id).all()
    
    for r in resources:
        print(f"\n[ID: {r.id}] Type: {r.resource_type} | Resource: {r.resource_id}")
        
        # Verify Encryption (It should look like a token, not dict)
        print(f"Stored (Encrypted): {r.compliance_metadata[:30]}...") 
        
        # Decrypt
        try:
            from app.utils.encryption import SecurityManager
            decrypted = SecurityManager.decrypt_metadata(r.compliance_metadata)
            print(f"Decrypted: {decrypted}")
            
            # Validation Check on Decrypted Data
            if "Owner" in decrypted:
                print("ALERT: PII 'Owner' found! Scrubbing failed.")
            if "Tags" in decrypted:
                print("ALERT: Noise 'Tags' found! Scrubbing failed.")
        except Exception as e:
            print(f"Decryption Failed: {e}")
            
    db.close()

if __name__ == "__main__":
    t_id = sys.argv[1] if len(sys.argv) > 1 else "default_tenant"
    retrieve_and_show(t_id)
