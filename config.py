"""
Configuration settings for Kana API
"""
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    API_TITLE: str = "Kana API"
    API_VERSION: str = "1.0.0"
    PORT: int = 8000
    ENVIRONMENT: str = "development"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # AI Configuration
    OPENAI_API_KEY: str = ""
    AI_MODEL: str = "gpt-4"
    
    # Solana Configuration
    SOLANA_RPC_URL: str = "https://api.mainnet-beta.solana.com"
    SOLANA_NETWORK: str = "mainnet-beta"
    
    # Security
    MAX_RISK_SCORE: float = 0.7
    THREAT_DETECTION_ENABLED: bool = True
    
    # JWT Authentication
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/auth/google/callback"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
