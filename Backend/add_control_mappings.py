"""
Add control_mappings table to track relationships between controls
"""
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, func
from app.database import Base, engine
# Import existing models so SQLAlchemy knows about them
from app.models import Control, Framework, User, Evidence

# Define the control_mappings table using the app's Base
class ControlMapping(Base):
    __tablename__ = 'control_mappings'
    
    id = Column(Integer, primary_key=True, index=True)
    source_control_id = Column(Integer, ForeignKey('controls.id'), nullable=False)
    target_control_id = Column(Integer, ForeignKey('controls.id'), nullable=False)
    mapping_type = Column(String, default='equivalent')  # equivalent, partial, related
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

def create_mappings_table():
    """Create the control_mappings table"""
    try:
        print("Creating control_mappings table...")
        Base.metadata.create_all(bind=engine)
        print("✓ Table created successfully!")
        print("\nMapping types:")
        print("- equivalent: Controls address the same requirement")
        print("- partial: Controls have some overlap")
        print("- related: Controls are related but different")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    create_mappings_table()