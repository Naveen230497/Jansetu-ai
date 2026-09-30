from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # App Config
    APP_NAME: str = "JanSetu AI Enterprise"
    VERSION: str = "2.0.0"
    ENVIRONMENT: str = "production"
    
    # Server Config
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # API Keys & Secrets
    GEMINI_API_KEY: str
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    
    # Security
    ALLOWED_ORIGINS: list[str] = ["*"]
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
