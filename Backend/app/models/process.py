from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.database import Base

# Association table for SubProcess <-> Control
process_control_mapping = Table(
    'process_control_mapping',
    Base.metadata,
    Column('subprocess_id', Integer, ForeignKey('sub_processes.id'), primary_key=True),
    Column('control_id', Integer, ForeignKey('controls.id'), primary_key=True)
)

class Process(Base):
    """
    Main business process (e.g., "Human Resources", "Software Development")
    """
    __tablename__ = "processes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False) # Removed unique=True to allow same names across frameworks if needed
    framework_code = Column(String, index=True, nullable=True, default="ISO27001") # Default to existing ISMS
    description = Column(Text, nullable=True)
    
    sub_processes = relationship("SubProcess", back_populates="process", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Process {self.name}>"

class SubProcess(Base):
    """
    Specific activity within a process (e.g., "Hiring", "Code Review")
    """
    __tablename__ = "sub_processes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    process_id = Column(Integer, ForeignKey("processes.id"), nullable=False)
    
    process = relationship("Process", back_populates="sub_processes")
    
    # Many-to-Many relationship with Controls
    controls = relationship("Control", secondary=process_control_mapping, backref="sub_processes")

    def __repr__(self):
        return f"<SubProcess {self.name} (Parent: {self.process_id})>"
