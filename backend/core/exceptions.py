"""自定义异常体系."""
from typing import Any, Optional


class FootballBaseError(Exception):
    code: str = "UNKNOWN"
    status_code: int = 500

    def __init__(self, message: str, code: Optional[str] = None, details: Optional[dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "details": self.details}


class SystemError(FootballBaseError):
    code = "SYSTEM_ERROR"
    status_code = 500


class ConfigError(SystemError):
    code = "CONFIG_ERROR"


class ThirdPartyError(FootballBaseError):
    code = "THIRD_PARTY_ERROR"
    status_code = 502

    def __init__(self, message: str, provider: str = "unknown", details: Optional[dict[str, Any]] = None) -> None:
        super().__init__(message, details=details)
        self.provider = provider


class LLMError(ThirdPartyError):
    code = "LLM_ERROR"

    def __init__(self, message: str, provider: str = "gemini", status_code: Optional[int] = None, details: Optional[dict[str, Any]] = None) -> None:
        super().__init__(message, provider=provider, details=details)
        if status_code is not None:
            self.status_code = status_code


class BusinessError(FootballBaseError):
    code = "BUSINESS_ERROR"
    status_code = 400


class ValidationError(BusinessError):
    code = "VALIDATION_ERROR"
    status_code = 422


class NotFoundError(BusinessError):
    code = "NOT_FOUND"
    status_code = 404


class DuplicateError(BusinessError):
    code = "DUPLICATE"
    status_code = 409


class PredictionError(BusinessError):
    code = "PREDICTION_ERROR"
