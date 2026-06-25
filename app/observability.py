"""Observability: structured JSON logs, request_id correlation, Prometheus metrics.

This module is self-contained so ``main.py`` stays small:

- ``configure_logging()``        installs a JSON log formatter on stdout.
- ``ObservabilityMiddleware``    adds a request_id, times each request, and
                                 records the HTTP metrics.
- ``feature_flag_changes_total`` counter is incremented by the app on a flag change.
- ``render_metrics()`` / ``METRICS_CONTENT_TYPE`` back the ``/metrics`` endpoint.
"""

import json
import logging
import sys
import time
import uuid
from contextvars import ContextVar

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

REQUEST_ID_HEADER = "X-Request-ID"

# Holds the current request's id so log records can pick it up automatically.
_request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")


# --------------------------------------------------------------------------- #
# Prometheus metrics
# --------------------------------------------------------------------------- #
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests.",
    ["method", "path", "status"],
)
http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds.",
    ["method", "path"],
)
feature_flag_changes_total = Counter(
    "feature_flag_changes_total",
    "Total number of feature flag changes.",
    ["flag"],
)

METRICS_CONTENT_TYPE = CONTENT_TYPE_LATEST


def render_metrics() -> bytes:
    """Render the current metrics in Prometheus text format."""
    return generate_latest()


# --------------------------------------------------------------------------- #
# Structured JSON logging
# --------------------------------------------------------------------------- #
class JsonFormatter(logging.Formatter):
    """Format log records as single-line JSON, including the request_id."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", _request_id_ctx.get()),
        }
        for key, value in getattr(record, "extra_fields", {}).items():
            payload[key] = value
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def configure_logging(level: int = logging.INFO) -> None:
    """Send JSON logs to stdout (idempotent)."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)


logger = logging.getLogger("app")


def current_request_id() -> str:
    """Return the request_id for the request currently being handled."""
    return _request_id_ctx.get()


# --------------------------------------------------------------------------- #
# Middleware
# --------------------------------------------------------------------------- #
class ObservabilityMiddleware(BaseHTTPMiddleware):
    """Assign a request_id, time the request, and record HTTP metrics."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex
        token = _request_id_ctx.set(request_id)
        start = time.perf_counter()
        try:
            response = await call_next(request)
            duration = time.perf_counter() - start

            # Use the route template (e.g. /flags/{name}) to keep label cardinality low.
            route = request.scope.get("route")
            path = getattr(route, "path", request.url.path)
            method = request.method
            status = response.status_code

            http_requests_total.labels(method=method, path=path, status=str(status)).inc()
            http_request_duration_seconds.labels(method=method, path=path).observe(duration)

            response.headers[REQUEST_ID_HEADER] = request_id
            logger.info(
                "request",
                extra={
                    "request_id": request_id,
                    "extra_fields": {
                        "method": method,
                        "path": path,
                        "status": status,
                        "duration_ms": round(duration * 1000, 2),
                    },
                },
            )
            return response
        finally:
            _request_id_ctx.reset(token)
