from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class TenantFramework(Base):
    """
    Links a Tenant to a Framework and tracks its active status.
    Many-to-Many relationship with extra attributes.
    """
    __tablename__ = "tenant_frameworks"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.internal_tenant_id"), nullable=False, index=True)
    framework_id = Column(Integer, ForeignKey("frameworks.id"), nullable=False, index=True)
    
    is_active = Column(Boolean, default=True) # Is this framework enabled for this tenant?
    is_locked = Column(Boolean, default=False) # Access Control: Can the tenant disable this? (Managed Service Provider feature)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    tenant = relationship("Tenant", backref="framework_links")
    framework = relationship("Framework")

    def __repr__(self):
        return f"<TenantFramework {self.tenant_id} -> {self.framework_id} (Active: {self.is_active})>"
