"""
Control Mapping Model - Maps relationships between controls across frameworks
"""
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base

class ControlMapping(Base):
    """Control mapping for cross-framework relationships"""
    
    __tablename__ = 'control_mappings'
    
    id = Column(Integer, primary_key=True, index=True)
    source_control_id = Column(Integer, ForeignKey('controls.id'), nullable=False)
    target_control_id = Column(Integer, ForeignKey('controls.id'), nullable=False)
    mapping_type = Column(String, default='equivalent')  # equivalent, partial, related
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    source_control = relationship("Control", foreign_keys=[source_control_id], back_populates="source_mappings")
    target_control = relationship("Control", foreign_keys=[target_control_id], back_populates="target_mappings")
    
    def __repr__(self):
        return f"<ControlMapping {self.source_control_id} → {self.target_control_id}>"