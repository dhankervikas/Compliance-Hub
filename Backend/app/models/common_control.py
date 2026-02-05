from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base

class CommonControl(Base):
    """
    Represents a unified control (e.g., 'Encryption at Rest') that maps
    to multiple framework-specific controls.
    """
    __tablename__ = "common_controls"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    domain = Column(String, index=True, nullable=False) # e.g., "Data Security", "Access Control"
    
    # Optional: Source of truth (e.g. SecureFrame ID or internal mapping ID)
    reference_id = Column(String, nullable=True) 

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<CommonControl {self.name}>"
