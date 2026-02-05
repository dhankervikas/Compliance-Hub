from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class TenantFeature(Base):
    """
    Tracks which features are enabled for a specific Tenant.
    e.g. 'aws_scanner', 'github_scanner', 'custom_reports'
    """
    __tablename__ = "tenant_features"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.internal_tenant_id"), nullable=False, index=True)
    feature_key = Column(String, nullable=False, index=True) # e.g. 'aws_scanner'
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    tenant = relationship("Tenant", backref="features")

    def __repr__(self):
        return f"<TenantFeature {self.tenant_id} -> {self.feature_key} (Active: {self.is_active})>"
