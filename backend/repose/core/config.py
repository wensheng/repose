from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Repose"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgres://repose:password@localhost:5544/repose"
    
    # Security
    SECRET_KEY: str = "superuser_secret_key_change_me_in_production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # LLM (Gemini)
    GEMINI_API_KEY: Optional[str] = None
    
    # GitHub PAT
    GITHUB_USERNAME: Optional[str] = None
    GITHUB_PAT: Optional[str] = None
    
    # GitHub App
    GITHUB_APP_ID: Optional[str] = None
    GITHUB_APP_PRIVATE_KEY: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
