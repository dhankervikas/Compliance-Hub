from pydantic_settings import BaseSettings
from typing import Optional, List, Any
from pydantic import field_validator, ValidationInfo
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    DATABASE_URL: str = f"sqlite:///{os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'sql_app.db')}"

    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    FIELD_ENCRYPTION_KEY: str = "W3pisde0nDHMsO1Cv7lfiqB8SpxdnH63R-cllQETyzM="
    APP_ENCRYPTION_KEY: str = "W3pisde0nDHMsO1Cv7lfiqB8SpxdnH63R-cllQETyzM="

    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Compliance Hub"
    VERSION: str = "1.0.0"

    APP_ENV: str = "development"
    PRODUCTION_DOMAIN: str = "https://app.assurisk.ai"

    @property
    def BASE_URL(self) -> str:
        if self.APP_ENV == "development":
            return "http://localhost:3000"
        return self.PRODUCTION_DOMAIN

    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:8000",
        "http://localhost:8001",
        "http://localhost:8002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8002",
        "https://compliance-hub-g1vy.vercel.app",
        "https://app.assurisk.ai",
	"https://w7rnfgfmhu.us-east-1.awsapprunner.com",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode='before')
    def assemble_cors_origins(cls, v: Any, info: ValidationInfo) -> Any:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    OPENAI_API_KEY: Optional[str] = None

    class Config:
        case_sensitive = True
        extra = "ignore"


settings = Settings()
