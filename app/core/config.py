from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "AI Knowledge Base"
    debug: bool = False
    environment: str = "development"
    
    # Database
    database_url: str
    
    # Security
    secret_key: str
    access_token_expire_minutes: int = 30
    
    # OpenAI
    openai_api_key: str
    
    # File Storage
    upload_directory: str = "./uploads"
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_file_types: list = [".pdf"]
    
    # Vector Database
    chroma_persist_directory: str = "./chroma_db"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Text Processing
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # AI Model Settings
    default_model: str = "gpt-3.5-turbo"
    embedding_model: str = "text-embedding-ada-002"
    max_tokens: int = 1000
    temperature: float = 0.7

    class Config:
        env_file = ".env"


settings = Settings()