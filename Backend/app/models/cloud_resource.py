from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base

class CloudResource(Base):
    """
    Stores scrubbed cloud resource configuration for compliance monitoring.
    Only contains keys relevant to security/compliance (e.g. encryption status).
    """
    __tablename__ = "cloud_resources"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, default="default_tenant", index=True, nullable=False)
    
    provider = Column(String, nullable=False) # aws, azure, gcp
    resource_type = Column(String, nullable=False) # s3_bucket, rds_instance
    resource_id = Column(String, nullable=False) # arn, etc.
    
    # The Scrubbed Data - ENCRYPTED (Stores Base64 String)
    compliance_metadata = Column(Text, nullable=False, default="")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<CloudResource {self.resource_type}:{self.resource_id}>"
