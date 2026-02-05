from sqlalchemy import Column, Integer, String, Text, Enum, JSON
from sqlalchemy.orm import relationship
import enum
from app.database import Base

class IntentStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"

class UniversalIntent(Base):
    """
    Root Entity for the Universal Intent Architecture.
    Acts as the single source of truth for compliance requirements across all standards.
    """
    __tablename__ = "universal_intents"
    
    id = Column(Integer, primary_key=True, index=True)
    intent_id = Column(String, unique=True, nullable=False, index=True) # e.g. "INT-001-ACCESS"
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False) # Maps to Canonical Process, e.g. "Access Control (IAM)"
    status = Column(Enum(IntentStatus), default=IntentStatus.PENDING)
    
    # Cache for performance (optional, stores list of linked standards)
    standard_mapping_json = Column(JSON, nullable=True) 

    # Relationships
    crosswalk_entries = relationship("IntentFrameworkCrosswalk", back_populates="intent", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<UniversalIntent {self.intent_id}: {self.category}>"
