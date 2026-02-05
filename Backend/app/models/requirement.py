from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum, JSON
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class RequirementMaster(Base):
    __tablename__ = "requirement_master"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, index=True)
    control_id = Column(String, index=True)
    control_title = Column(String)
    requirement_text = Column(Text, nullable=False)
    
    # Target Control (e.g. ISO 42001 B.7.2) - derived or mapped
    target_control = Column(String, index=True, nullable=True)
    
    # Module Source (Filename)
    module_source = Column(String, index=True)

    # Relationships
    status_entry = relationship("RequirementStatus", back_populates="requirement", uselist=False)

    def __repr__(self):
        return f"<Requirement {self.control_id} from {self.module_source}>"

class RequirementStatus(Base):
    __tablename__ = "requirement_status"

    id = Column(Integer, primary_key=True, index=True)
    requirement_id = Column(Integer, ForeignKey("requirement_master.id"), unique=True)
    
    status = Column(String, default="GAP") # 'MET', 'GAP', 'PARTIAL'
    
    # Link to the User's Policy content that satisfies this
    mapped_policy_id = Column(Integer, ForeignKey("policies.id"), nullable=True)
    mapped_section = Column(String, nullable=True) # e.g. "Section 3.1"
    
    last_verified = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Metadata for the "Audit Proof"
    verification_metadata = Column(JSON, default={}) # { "author": "system", "version": "1.0" }

    requirement = relationship("RequirementMaster", back_populates="status_entry")
    policy = relationship("app.models.policy.Policy") # Lazy string import to avoid circular dep if needed

    def __repr__(self):
        return f"<Status {self.status} for Req {self.requirement_id}>"
