from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.database import Base
import uuid

class Tenant(Base):
    """
    Tenant model to manage multi-tenancy configurations, keys, and metadata.
    """
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    internal_tenant_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Security
    encryption_key = Column(String, nullable=False) # AES-256 Key for this tenant
    
    # Metadata (ISO 42001 Context, Subscription info, etc.)
    metadata_json = Column(JSON, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Tenant {self.name} ({self.slug})>"
