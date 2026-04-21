from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # 数据库
    database_url: str = "sqlite+aiosqlite:///./hr.db"
    
    # AI 配置（可选）
    default_llm_provider: Optional[str] = None
    default_llm_api_key: Optional[str] = None
    default_llm_model: Optional[str] = None
    
    # 文件上传
    max_file_size: int = 20971520  # 20MB
    max_files_per_upload: int = 50
    
    # 应用配置
    app_name: str = "人力资源招聘智能辅助工具"
    debug: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
