"""LLM Service - Gemini provider."""
from typing import Any
from config import settings
from utils.http_client import HttpClient
from utils.logger import get_logger
from core.exceptions import LLMError

_logger = get_logger("llm")


class GeminiProvider:
    name = "gemini"

    def __init__(self) -> None:
        self._api_key = settings.gemini_api_key
        self._base = settings.gemini_base_url
        self._model = settings.gemini_model
        self._client = HttpClient(base_url=self._base, timeout=60)

    def chat(self, messages: list[dict[str, str]], temperature: float = 0.7, max_tokens: int = 2048) -> str:
        if not self._api_key:
            raise LLMError("GEMINI_API_KEY not set", provider="gemini")

        contents = []
        for msg in messages:
            role = msg.get("role", "user")
            text = msg.get("content", "")
            if role == "system":
                contents.append({"role": "user", "parts": [{"text": f"[System] {text}"}]})
            elif role == "assistant":
                contents.append({"role": "model", "parts": [{"text": text}]})
            else:
                contents.append({"role": "user", "parts": [{"text": text}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
                "topP": 0.95,
            },
        }

        path = f"models/{self._model}:generateContent?key={self._api_key}"
        try:
            resp = self._client._request("POST", path, json=payload, headers={"Content-Type": "application/json"})
            data = resp.json()
            candidates = data.get("candidates", [])
            if not candidates:
                raise LLMError(f"Gemini blocked: {data.get('promptFeedback', {}).get('blockReason', 'unknown')}", provider="gemini")
            parts = candidates[0].get("content", {}).get("parts", [])
            if not parts:
                raise LLMError("Gemini empty response", provider="gemini")
            return parts[0].get("text", "")
        except LLMError:
            raise
        except Exception as e:
            raise LLMError(f"Gemini API call failed: {e}", provider="gemini")

    def chat_with_prompt(self, system: str, user: str, temperature: float = 0.7, max_tokens: int = 2048) -> str:
        return self.chat([{"role": "system", "content": system}, {"role": "user", "content": user}], temperature, max_tokens)


class LLMService:
    _instance: Any = None

    @classmethod
    def get_instance(cls) -> "LLMService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        self._provider = GeminiProvider()
        _logger.info(f"LLM service initialized provider={self._provider.name}")

    def chat(self, messages: list[dict], temperature: float = 0.7, max_tokens: int = 2048) -> str:
        _logger.info(f"llm request provider={self._provider.name} messages={len(messages)}")
        result = self._provider.chat(messages, temperature, max_tokens)
        _logger.debug(f"llm response provider={self._provider.name} length={len(result)}")
        return result

    def chat_with_prompt(self, system: str, user: str, temperature: float = 0.7, max_tokens: int = 2048) -> str:
        return self.chat([{"role": "system", "content": system}, {"role": "user", "content": user}], temperature, max_tokens)
