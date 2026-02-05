from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base

class MasterTemplate(Base):
    __tablename__ = "master_templates"

    id = Column(Integer, primary_key=True, index=True)
    control_id = Column(String, index=True, nullable=True) # e.g. "A.5.15"
    title = Column(String, index=True) # Policy Name
    content = Column(Text) # Extracted HTML/Markdown
    original_filename = Column(String) # For traceability
    is_immutable = Column(Boolean, default=True) # Security Guardrail
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
