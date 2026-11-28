"""Request tracking middleware for request IDs, duration measurement, and structured logging.

Provides:
- Unique request ID generation and propagation
- Request duration measurement with monotonic timer
- In-memory duration storage grouped by route
- Structured logging per request
- Exception safety for all request types
"""

import json
import logging
import re
import time
import uuid
from collections import defaultdict
from threading import Lock
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.routing import Match

logger = logging.getLogger(__name__)

# Request ID validation pattern: alphanumeric, hyphens, max 100 chars
REQUEST_ID_PATTERN = re.compile(r"^[a-zA-Z0-9\-]{1,100}$")

# Maximum stored requests per route (prevent unbounded memory growth)
MAX_DURATIONS_PER_ROUTE = 1000


class RequestDurationStore:
    """Thread-safe in-memory storage for request durations grouped by route.
    
    Stores durations in milliseconds, grouped by route template.
    Implements bounded storage to prevent memory exhaustion.
    """
    
    def __init__(self, max_per_route: int = MAX_DURATIONS_PER_ROUTE):
        """Initialize the duration store.
        
        Args:
            max_per_route: Maximum durations to store per route
        """
        self._durations: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()
        self._max_per_route = max_per_route
    
    def record(self, route: str, duration_ms: float) -> None:
        """Record a request duration for a specific route.
        
        Args:
            route: Route template (e.g., "/api/v1/listings/{id}")
            duration_ms: Request duration in milliseconds
        """
        with self._lock:
            route_durations = self._durations[route]
            route_durations.append(duration_ms)
            
            # Bounded storage: keep only the most recent N durations
            if len(route_durations) > self._max_per_route:
                # Remove oldest 10% to reduce lock contention
                remove_count = self._max_per_route // 10
                self._durations[route] = route_durations[remove_count:]
    
    def get_all(self) -> dict[str, list[float]]:
        """Get all stored durations grouped by route.
        
        Returns:
            Dictionary mapping route templates to lists of durations in ms
        """
        with self._lock:
            # Return a deep copy to prevent external modification
            return {route: list(durations) for route, durations in self._durations.items()}
    
    def get_route(self, route: str) -> list[float]:
        """Get durations for a specific route.
        
        Args:
            route: Route template
            
        Returns:
            List of durations in milliseconds (copy)
        """
        with self._lock:
            return list(self._durations.get(route, []))
    
    def clear(self) -> None:
        """Clear all stored durations. For testing purposes."""
        with self._lock:
            self._durations.clear()


# Global duration store instance
_duration_store = RequestDurationStore()


def get_duration_store() -> RequestDurationStore:
    """Get the global request duration store.
    
    Returns:
        RequestDurationStore instance
    """
    return _duration_store


def _validate_request_id(request_id: str | None) -> str | None:
    """Validate an incoming request ID.
    
    Args:
        request_id: Request ID from X-Request-ID header
        
    Returns:
        Validated request ID or None if invalid
    """
    if not request_id:
        return None
    
    # Check pattern and length
    if REQUEST_ID_PATTERN.match(request_id):
        return request_id
    
    return None


def _generate_request_id() -> str:
    """Generate a new unique request ID.
    
    Returns:
        UUID4 string
    """
    return str(uuid.uuid4())


def _get_route_template(request: Request) -> str:
    """Extract the route template from the request.
    
    Uses Starlette's route matching to get the template path.
    Falls back to the actual path if template is unavailable.
    
    Args:
        request: FastAPI Request instance
        
    Returns:
        Route template (e.g., "/api/v1/listings/{id}") or actual path
    """
    # Try to match route and get template
    for route in request.app.routes:
        match, _ = route.matches(request.scope)
        if match == Match.FULL:
            # Get the path pattern/template
            if hasattr(route, "path"):
                return route.path
            break
    
    # Fallback to actual path
    return request.url.path


def _sanitize_for_logging(value: str, max_length: int = 200) -> str:
    """Sanitize a string value for safe logging.
    
    Truncates long values to prevent log bloat.
    
    Args:
        value: String to sanitize
        max_length: Maximum length
        
    Returns:
        Sanitized string
    """
    if len(value) > max_length:
        return value[:max_length] + "..."
    return value


class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware for request tracking, duration measurement, and structured logging.
    
    Responsibilities:
    - Generate or validate request ID
    - Measure request duration
    - Store durations for metrics
    - Log structured request information
    - Propagate request ID in response header
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process each request with tracking and logging.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware or endpoint handler
            
        Returns:
            HTTP response with X-Request-ID header
        """
        # 1. Generate or validate request ID
        incoming_request_id = request.headers.get("x-request-id")
        validated_id = _validate_request_id(incoming_request_id)
        request_id = validated_id if validated_id else _generate_request_id()
        
        # Store in request state for access by exception handlers and endpoints
        request.state.request_id = request_id
        
        # 2. Start duration measurement (monotonic timer)
        start_time = time.perf_counter()
        
        # 3. Process request - call_next handles exceptions internally
        # and returns error responses created by exception handlers
        response = await call_next(request)
        status_code = response.status_code
        
        # 4. Measure duration
        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000  # Convert to milliseconds
        
        # 5. Get route template for grouping
        route_template = _get_route_template(request)
        
        # 6. Store duration for metrics
        _duration_store.record(route_template, duration_ms)
        
        # 7. Structured logging (JSON-compatible format)
        log_data = {
            "request_id": request_id,
            "method": request.method,
            "path": _sanitize_for_logging(request.url.path),
            "route": route_template,
            "status_code": status_code,
            "duration_ms": round(duration_ms, 2),
        }
        
        # Log at appropriate level based on status
        if status_code >= 500:
            logger.error("Request completed with server error", extra=log_data)
        elif status_code >= 400:
            logger.warning("Request completed with client error", extra=log_data)
        else:
            logger.info("Request completed successfully", extra=log_data)
        
        # 8. Add request ID to response header
        response.headers["X-Request-ID"] = request_id
        
        return response
