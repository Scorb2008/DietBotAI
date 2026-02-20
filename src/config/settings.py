import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Bot configuration settings"""
    
    # Bot token from BotFather
    BOT_TOKEN: str
    
    # Admin user ID (Telegram user ID)
    ADMIN_ID: int
    
    # Mistral AI API key
    MISTRAL_API_KEY: str
    
    # Database settings
    DB_PATH: Path = Path("data/bot.db")
    
    # AI settings
    MAX_REQUESTS_PER_USER: int = 10
    MISTRAL_MODEL: str = "mistral-large-latest"
    MISTRAL_MAX_TOKENS: int = 500
    
    # Bot settings
    REQUEST_TIMEOUT: int = 30
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create data directory if it doesn't exist
        self.DB_PATH.parent.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()