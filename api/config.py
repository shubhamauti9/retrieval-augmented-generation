from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional

"""
API Configuration Settings
Application settings loaded from environment variables
"""
class Settings(BaseSettings):
    """
    API Settings
    """
    app_name: str = "RAG Pipeline API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    """
    Data paths
    """
    data_dir: Path = Path("./data")
    vector_store_dir: Path = Path("./data/vector_store")
    uploads_dir: Path = Path("./data/uploads")
    
    """
    Embedding model
    """
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dim: int = 384
    
    """
    LLM settings
    """
    llm_model: str = "llama3.2"
    llm_base_url: str = "http://localhost:11434" #if using locally hosted model
    
    """
    Chunking settings
    """
    chunk_size: int = 500
    chunk_overlap: int = 100
    
    """
    Retrieval settings
    """
    default_top_k: int = 5
    
    """
    Redis settings
    """
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_enabled: bool = True
    
    """
    Cache settings
    """
    embedding_cache_ttl: int = 86400 * 7    #7days
    query_cache_ttl: int = 3600             #1hour
    rate_limit_requests: int = 100
    rate_limit_window: int = 60             #1minute
    
    class Config:
        env_prefix = "RAG_"
        env_file = ".env"


"""
Global settings instance
"""
settings = Settings()

"""
Ensure directories exist
"""
settings.data_dir.mkdir(parents=True, exist_ok=True)
settings.vector_store_dir.mkdir(parents=True, exist_ok=True)
settings.uploads_dir.mkdir(parents=True, exist_ok=True)
