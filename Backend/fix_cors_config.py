
import os

file_path = r"..\..\Backend\AssuRisk\app\config.py"

# Using single quotes for the outer wrapper to avoid conflict with docstrings
content = r'''from pydantic_settings import BaseSettings
from typing import Optional, List, Any
from pydantic import field_validator, ValidationInfo

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    # Default to sqlite for local dev if not set
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    
    # Security
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Compliance Hub"
    VERSION: str = "1.0.0"
    
    # CORS
    # Allow all for Vercel/Render ease of use
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    @field_validator("BACKEND_CORS_ORIGINS", mode='before')
    def assemble_cors_origins(cls, v: Any, info: ValidationInfo) -> Any:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # AI
    GEMINI_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
'''

try:
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"SUCCESS: Updated {os.path.abspath(file_path)}")
except Exception as e:
    print(f"ERROR: Failed to update file. {e}")
