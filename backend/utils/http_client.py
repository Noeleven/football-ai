"""HTTP client with retry + timeout + masking."""
import requests
from typing import Any, Optional
from utils.logger import get_logger
from core.exceptions import ThirdPartyError

_logger = get_logger(__name__)
_SENSITIVE_HEADERS = {"authorization", "x-api-key", "api-key", "bearer"}


def _mask_headers(h: Optional[dict]) -> dict:
    if not h:
        return {}
    return {k: "***" if k.lower() in _SENSITIVE_HEADERS else v for k, v in h.items()}


class HttpClient:
    def __init__(self, base_url: str = "", timeout: int = 30, max_retries: int = 3) -> None:
        self._base = base_url
        self._timeout = timeout
        self._max_retries = max_retries

    def _request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        url = path if path.startswith("http") else self._base.rstrip("/") + "/" + path.lstrip("/")
        kw = dict(kwargs)
        kw.setdefault("timeout", self._timeout)
        _logger.debug(f"http {method} {url} headers={_mask_headers(kw.get('headers'))}")
        last_exc: Optional[Exception] = None
        for attempt in range(1, self._max_retries + 1):
            try:
                resp = requests.request(method, url, **kw)
                if 200 <= resp.status_code < 300:
                    return resp
                if 400 <= resp.status_code < 500:
                    raise ThirdPartyError(f"HTTP {resp.status_code} {url}", details={"status": resp.status_code})
                raise requests.HTTPError(f"HTTP {resp.status_code}", response=resp)
            except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as e:
                last_exc = e
                if attempt == self._max_retries:
                    break
                import time, random
                delay = min(1.0 * (2 ** (attempt - 1)), 30.0) * (0.5 + random.random())
                _logger.warn(f"retry {attempt}/{self._max_retries} error={e}")
                time.sleep(delay)
            except Exception as e:
                raise ThirdPartyError(f"HTTP {method} {url} failed: {e}")
        raise ThirdPartyError(f"HTTP {method} {url} failed after {self._max_retries} attempts", details={"error": str(last_exc)})

    def get(self, path: str, **kw: Any) -> requests.Response:
        return self._request("GET", path, **kw)

    def post(self, path: str, **kw: Any) -> requests.Response:
        return self._request("POST", path, **kw)

    def get_json(self, path: str, **kw: Any) -> dict:
        return self.get(path, **kw).json()

    def post_json(self, path: str, **kw: Any) -> dict:
        return self.post(path, **kw).json()
