from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

class Settings(BaseSettings):
    app_name: str = "AI Knowledge Base"
    debug: bool = False
    environment: str = "development"
    
    # Supabase
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "test-secret-key")
    access_token_expire_minutes: int = 30
    
    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # File Storage
    upload_directory: str = os.getenv("UPLOAD_DIRECTORY", "./uploads")
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_file_types: list = [".pdf"]
    
    # Vector Database
    chroma_persist_directory: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
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
        env_file_encoding = "utf-8"


settings = Settings()