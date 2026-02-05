from app.database import engine, Base
from app.models.cloud_resource import CloudResource
from app.models.compliance_result import ComplianceResult

print("Creating CloudResource schema...")
Base.metadata.create_all(bind=engine)
print("Done.")
