import logging
import sys
from typing import Any

import structlog

SENSITIVE_KEYS = {
    "cookie",
    "cookies",
    "li_at",
    "session_cookie",
    "csrf_token",
    "jsessionid",
    "authorization",
    "token",
    "password",
    "secret",
}


def redact_sensitive_data(
    logger: Any, method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Structlog processor to recursively redact sensitive keys from log event dicts."""
    return _redact_dict(event_dict)


def _redact_dict(data: dict[str, Any]) -> dict[str, Any]:
    cleaned: dict[str, Any] = {}
    for key, value in data.items():
        key_lower = str(key).lower()
        if any(sensitive in key_lower for sensitive in SENSITIVE_KEYS):
            cleaned[key] = "[REDACTED]"
        elif isinstance(value, dict):
            cleaned[key] = _redact_dict(value)
        elif isinstance(value, list):
            cleaned[key] = [
                _redact_dict(item) if isinstance(item, dict) else item for item in value
            ]
        else:
            cleaned[key] = value
    return cleaned


def setup_logging(log_level: str = "INFO") -> None:
    """Configures structured JSON logging with structlog and Python standard logging."""
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=numeric_level,
    )

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        redact_sensitive_data,
        structlog.processors.JSONRenderer(),
    ]

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = "app") -> structlog.stdlib.BoundLogger:
    """Returns a bound structlog logger."""
    return structlog.get_logger(name)
