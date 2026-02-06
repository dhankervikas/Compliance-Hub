import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum as SqEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class SourceType(str, enum.Enum):
    AZURE_AD = "azure_ad"
    GOOGLE_WORKSPACE = "google_workspace"
    MANUAL_IMPORT = "manual_import"


class EmploymentStatus(str, enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    CONTRACTOR = "Contractor"


class Person(Base):
    __tablename__ = "people"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    source = Column(String, default=SourceType.MANUAL_IMPORT)
    external_id = Column(String, nullable=True)
    employment_status = Column(String, default=EmploymentStatus.ACTIVE)
    job_title = Column(String, nullable=True)
    department = Column(String, nullable=True)
    tenant_id = Column(String, ForeignKey("tenants.internal_tenant_id"), nullable=False, default="default")
    last_synced_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    assigned_controls = relationship("Control", back_populates="owner_rel")
