from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy import UniqueConstraint
from app.database import Base


class User(Base):
    """User model for authentication and user management"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    tenant_id = Column(String, default="default_tenant", index=True, nullable=False)
    full_name = Column(String, nullable=True)
    
    role = Column(String, default="user")
    allowed_frameworks = Column(String, default="ALL") # Comma-separated list: "ISO27001,SOC2"
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('username', 'tenant_id', name='unique_username_per_tenant'),
    )
    
    def __repr__(self):
        return f"<User {self.username}>"