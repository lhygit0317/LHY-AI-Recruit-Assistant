"""核心配置模块。"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置，从环境变量 / .env 加载。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str = "postgresql+psycopg://lhy@localhost:5432/recruit_assistant"

    # JWT
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 24

    # LLM
    deepseek_api_key: str | None = None
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    default_llm_provider: str = "deepseek"
    default_llm_model: str = "deepseek-chat"

    # Storage
    resume_storage_dir: Path = Path("./data/resumes")
    max_resume_size_mb: int = 10

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """获取单例配置。"""
    s = Settings()
    s.resume_storage_dir.mkdir(parents=True, exist_ok=True)
    return s