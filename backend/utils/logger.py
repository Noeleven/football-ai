"""Structured logging with trace context and sensitive data masking."""
import logging, json, sys, re, uuid
from datetime import datetime, timezone
from typing import Any, Optional
from contextvars import ContextVar

_trace_var: ContextVar[str] = ContextVar("trace_id", default="")
_task_var: ContextVar[str] = ContextVar("task_id", default="")


def new_trace_id() -> str:
    return str(uuid.uuid4())[:16]


def new_task_id(prefix: str = "task") -> str:
    ts = datetime.now(timezone.utc).strftime("%m%d%H%M%S")
    return f"{prefix}-{ts}-{uuid.uuid4().hex[:6]}"


def set_trace(trace_id: str = "", task_id: str = "") -> None:
    if trace_id:
        _trace_var.set(trace_id)
    if task_id:
        _task_var.set(task_id)


_SENSITIVE: list[tuple[str, str]] = [
    (r"(api[_-]?key)\s*[:=]\s*['\"]?[\w\-]+['\"]?", r"\1: ***"),
    (r"(bearer|token|secret)\s+[\w.\-]+", r"\1 ***"),
    (r"1[3-9]\d{9}", "***PHONE***"),
]


def _mask(s: str) -> str:
    for pat, repl in _SENSITIVE:
        s = re.sub(pat, repl, s, flags=re.IGNORECASE)
    return s


class JsonFormatter(logging.Formatter):
    def format(self, rec: logging.LogRecord) -> str:
        obj = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": rec.levelname,
            "logger": rec.name,
            "message": _mask(rec.getMessage()),
            "trace_id": _trace_var.get() or "",
            "task_id": _task_var.get() or "",
        }
        if rec.exc_info:
            obj["exc"] = self.formatException(rec.exc_info)
        if hasattr(rec, "duration_ms"):
            obj["duration_ms"] = rec.duration_ms
        return json.dumps(obj, ensure_ascii=False, default=str)


class PlainFormatter(logging.Formatter):
    def format(self, rec: logging.LogRecord) -> str:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        ctx = f"[{_trace_var.get()}]" if _trace_var.get() else ""
        return f"{ts} {rec.levelname:5s} {ctx} {rec.name}: {_mask(rec.getMessage())}"


_LOGGERS: dict[str, logging.Logger] = {}


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    if name not in _LOGGERS:
        lg = logging.getLogger(name)
        lvl = getattr(logging, (level or "INFO"), logging.INFO)
        lg.setLevel(lvl)
        if not lg.handlers:
            h = logging.StreamHandler(sys.stdout)
            h.setFormatter(PlainFormatter() if level == "DEBUG" else JsonFormatter())
            lg.addHandler(h)
        lg.propagate = False
        _LOGGERS[name] = lg
    return _LOGGERS[name]
