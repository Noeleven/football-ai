"""Redis cache service with pub/sub support."""
import json
import redis
from typing import Any, Optional
from utils.logger import get_logger

_logger = get_logger("redis_service")


class RedisService:
    _instance: Optional["RedisService"] = None

    @classmethod
    def get_instance(cls) -> "RedisService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        from core.config import config
        self._prefix = config.redis_prefix
        try:
            self._client = redis.Redis(
                host=config.redis_host,
                port=config.redis_port,
                db=0,
                decode_responses=True,
                socket_connect_timeout=5,
            )
            self._client.ping()
            _logger.info("Redis connected")
        except redis.ConnectionError:
            _logger.warn("Redis unavailable, running without cache")
            self._client = None

    def _key(self, key: str) -> str:
        return f"{self._prefix}{key}"

    def get(self, key: str) -> Optional[str]:
        if not self._client:
            return None
        try:
            return self._client.get(self._key(key))
        except redis.RedisError as e:
            _logger.warn(f"redis get failed: {e}")
            return None

    def set(self, key: str, value: str, ttl: int = 3600) -> None:
        if not self._client:
            return
        try:
            self._client.setex(self._key(key), ttl, value)
        except redis.RedisError as e:
            _logger.warn(f"redis set failed: {e}")

    def delete(self, key: str) -> None:
        if not self._client:
            return
        try:
            self._client.delete(self._key(key))
        except redis.RedisError as e:
            _logger.warn(f"redis delete failed: {e}")

    def get_json(self, key: str) -> Optional[dict[str, Any]]:
        raw = self.get(key)
        if raw:
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                pass
        return None

    def set_json(self, key: str, value: dict[str, Any], ttl: int = 3600) -> None:
        self.set(key, json.dumps(value, ensure_ascii=False, default=str), ttl)

    def publish(self, channel: str, message: dict[str, Any]) -> None:
        if not self._client:
            return
        try:
            self._client.publish(self._key(channel), json.dumps(message, default=str))
        except redis.RedisError as e:
            _logger.warn(f"redis publish failed: {e}")

    def subscribe(self, channel: str):
        if not self._client:
            return None
        pubsub = self._client.pubsub()
        pubsub.subscribe(self._key(channel))
        return pubsub

    def cache_match(self, match_id: str, data: dict[str, Any], ttl: int = 1800) -> None:
        self.set_json(f"match:{match_id}", data, ttl)

    def get_cached_match(self, match_id: str) -> Optional[dict[str, Any]]:
        return self.get_json(f"match:{match_id}")

    def cache_prediction(self, match_id: str, data: dict[str, Any], ttl: int = 3600) -> None:
        self.set_json(f"prediction:{match_id}", data, ttl)

    def get_cached_prediction(self, match_id: str) -> Optional[dict[str, Any]]:
        return self.get_json(f"prediction:{match_id}")

    def cache_news_list(self, key: str, data: list[dict[str, Any]], ttl: int = 600) -> None:
        self.set_json(f"news:list:{key}", data, ttl)

    def get_cached_news_list(self, key: str) -> Optional[list[dict[str, Any]]]:
        return self.get_json(f"news:list:{key}")

    def invalidate_pattern(self, pattern: str) -> None:
        if not self._client:
            return
        try:
            keys = self._client.keys(self._key(pattern))
            if keys:
                self._client.delete(*keys)
        except redis.RedisError as e:
            _logger.warn(f"redis invalidate failed: {e}")