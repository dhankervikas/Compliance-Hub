from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Framework(Base):
    """Framework model for compliance frameworks"""
    
    __tablename__ = "frameworks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    code = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    version = Column(String, nullable=True)
    tenant_id = Column(String, default="default_tenant", nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    controls = relationship("Control", back_populates="framework", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Framework {self.name}>"