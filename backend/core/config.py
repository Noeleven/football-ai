"""Configuration loader from config.yaml."""
import os
import yaml
from typing import Any, Optional
from pathlib import Path


class Config:
    _instance: Optional["Config"] = None
    _data: dict[str, Any] = {}

    @classmethod
    def get_instance(cls) -> "Config":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        config_path = os.environ.get("CONFIG_PATH", "config.yaml")
        if not Path(config_path).is_absolute():
            config_path = Path(__file__).parent.parent / config_path
        if Path(config_path).exists():
            with open(config_path) as f:
                self._data = yaml.safe_load(f) or {}
        else:
            self._data = self._default_config()

    def _default_config(self) -> dict[str, Any]:
        return {
            "app": {"name": "Football AI Platform", "debug": False, "log_level": "INFO"},
            "database": {"provider": "sqlite", "path": "data/football.db"},
            "redis": {"host": "localhost", "port": 6379, "db": 0, "prefix": "football_ai:"},
            "llm": {"provider": "gemini", "gemini": {"api_key": "", "base_url": "https://generativelanguage.googleapis.com/v1beta", "model": "gemini-2.0-flash"}, "openai": {"api_key": "", "base_url": "https://api.openai.com/v1", "model": "gpt-4o"}},
            "http": {"timeout": 30, "max_retries": 3},
            "cache": {"enable": True, "ttl_seconds": 3600},
            "prediction": {"weights": {"form": 0.25, "head_to_head": 0.20, "home_away": 0.15, "injury": 0.15, "tactics": 0.25}, "confidence_thresholds": {"high": 0.75, "medium": 0.55}, "timeout": 60, "max_retries": 3},
        }

    def get(self, *keys: str, default: Any = None) -> Any:
        val = self._data
        for k in keys:
            if isinstance(val, dict):
                val = val.get(k)
                if val is None:
                    return default
            else:
                return default
        return val

    @property
    def app_name(self) -> str:
        return self.get("app", "name", default="Football AI Platform")

    @property
    def debug(self) -> bool:
        return self.get("app", "debug", default=False)

    @property
    def log_level(self) -> str:
        return self.get("app", "log_level", default="INFO")

    @property
    def db_provider(self) -> str:
        return self.get("database", "provider", default="sqlite")

    @property
    def db_path(self) -> str:
        return self.get("database", "path", default="data/football.db")

    @property
    def redis_host(self) -> str:
        return self.get("redis", "host", default="localhost")

    @property
    def redis_port(self) -> int:
        return self.get("redis", "port", default=6379)

    @property
    def redis_prefix(self) -> str:
        return self.get("redis", "prefix", default="football_ai:")

    @property
    def cache_enabled(self) -> bool:
        return self.get("cache", "enable", default=True)

    @property
    def cache_ttl(self) -> int:
        return self.get("cache", "ttl_seconds", default=3600)

    @property
    def llm_provider(self) -> str:
        return self.get("llm", "provider", default="gemini")

    @property
    def gemini_api_key(self) -> str:
        # 优先从环境变量读取，fallback到配置文件
        return os.environ.get("GEMINI_API_KEY") or self.get("llm", "gemini", "api_key", default="")

    @property
    def gemini_base_url(self) -> str:
        return os.environ.get("GEMINI_BASE_URL") or self.get("llm", "gemini", "base_url", default="https://generativelanguage.googleapis.com/v1beta")

    @property
    def gemini_model(self) -> str:
        return os.environ.get("GEMINI_MODEL") or self.get("llm", "gemini", "model", default="gemini-2.0-flash")

    @property
    def deepseek_api_key(self) -> str:
        return os.environ.get("DEEPSEEK_API_KEY") or self.get("llm", "deepseek", "api_key", default="")

    @property
    def deepseek_base_url(self) -> str:
        return os.environ.get("DEEPSEEK_BASE_URL") or self.get("llm", "deepseek", "base_url", default="https://api.deepseek.com/v1")

    @property
    def deepseek_model(self) -> str:
        return os.environ.get("DEEPSEEK_MODEL") or self.get("llm", "deepseek", "model", default="deepseek-v4-flash")


config = Config.get_instance()