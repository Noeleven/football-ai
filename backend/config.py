"""Football AI Platform - 配置层."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_prefix="FOOTBALL_")

    app_name: str = "Football AI Platform"
    debug: bool = False
    log_level: Literal["DEBUG", "INFO", "WARN", "ERROR"] = "INFO"

    # LLM - Gemini (default)
    llm_provider: Literal["gemini", "openai"] = "gemini"
    gemini_api_key: str = ""
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    gemini_model: str = "gemini-2.0-flash"

    # LLM - OpenAI (backup)
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o"

    # HTTP
    http_timeout: int = 30
    http_max_retries: int = 3
    http_retry_base_delay: float = 1.0

    # Database
    db_path: str = "data/football.db"

    # Cache
    enable_cache: bool = True
    cache_ttl_seconds: int = 3600

    # Prediction weights
    weight_form: float = 0.25
    weight_head_to_head: float = 0.20
    weight_home_away: float = 0.15
    weight_injury: float = 0.15
    weight_tactics: float = 0.25

    # Confidence thresholds
    confidence_high: float = 0.75
    confidence_medium: float = 0.55

    # AI prediction settings
    prediction_timeout: int = 60
    max_retries_per_prediction: int = 3


settings = Settings()
