"""Centralized API exception handling and error response formatting.

All API errors follow a standard envelope format with consistent error codes
and request IDs for traceability.
"""

import logging
import uuid
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class ErrorDetail(BaseModel):
    """Standard error detail structure."""
    code: str
    message: str
    request_id: str


class ErrorResponse(BaseModel):
    """Standard error response envelope."""
    error: ErrorDetail


# HTTP status code to error code mapping
STATUS_CODE_TO_ERROR_CODE = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    409: "conflict",
    422: "validation_error",
    429: "too_many_requests",
    500: "internal_error",
}


def _get_request_id(request: Request) -> str:
    """Extract or generate request ID.
    
    Priority:
    1. Use existing request ID from request.state if middleware set it
    2. Use X-Request-ID header if present
    3. Generate new UUID as fallback
    
    Args:
        request: FastAPI Request instance
        
    Returns:
        Request ID string
    """
    # Check if middleware already set request_id in request.state
    if hasattr(request.state, "request_id"):
        return request.state.request_id
    
    # Check for X-Request-ID header
    request_id = request.headers.get("x-request-id")
    if request_id:
        return request_id
    
    # Fallback: generate new UUID
    return str(uuid.uuid4())


def _create_error_response(
    status_code: int,
    message: str,
    request_id: str,
) -> JSONResponse:
    """Create standardized error response.
    
    Args:
        status_code: HTTP status code
        message: Error message
        request_id: Request tracking ID
        
    Returns:
        JSONResponse with standard error envelope and X-Request-ID header
    """
    error_code = STATUS_CODE_TO_ERROR_CODE.get(status_code, "internal_error")
    
    response = ErrorResponse(
        error=ErrorDetail(
            code=error_code,
            message=message,
            request_id=request_id,
        )
    )
    
    json_response = JSONResponse(
        status_code=status_code,
        content=response.model_dump(),
    )
    
    # Add X-Request-ID header to error responses
    json_response.headers["X-Request-ID"] = request_id
    
    return json_response


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTPException.
    
    Converts HTTPException to standard error envelope format.
    
    Args:
        request: FastAPI Request
        exc: HTTPException instance
        
    Returns:
        JSONResponse with standard error format
    """
    request_id = _get_request_id(request)
    
    # Log the error with context
    logger.warning(
        "HTTP exception occurred",
        extra={
            "request_id": request_id,
            "status_code": exc.status_code,
            "detail": exc.detail,
            "path": request.url.path,
            "method": request.method,
        }
    )
    
    return _create_error_response(
        status_code=exc.status_code,
        message=str(exc.detail),
        request_id=request_id,
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Handle Pydantic/FastAPI validation errors.
    
    Returns HTTP 422 with standard error envelope.
    
    Args:
        request: FastAPI Request
        exc: RequestValidationError instance
        
    Returns:
        JSONResponse with validation error details
    """
    request_id = _get_request_id(request)
    
    # Extract first validation error for the message
    errors = exc.errors()
    if errors:
        first_error = errors[0]
        # Format: "field_name: error_message"
        field = ".".join(str(loc) for loc in first_error.get("loc", []))
        error_msg = first_error.get("msg", "Validation error")
        message = f"{field}: {error_msg}" if field else error_msg
    else:
        message = "Validation error"
    
    # Log validation errors
    logger.warning(
        "Validation error occurred",
        extra={
            "request_id": request_id,
            "errors": errors,
            "path": request.url.path,
            "method": request.method,
        }
    )
    
    return _create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message=message,
        request_id=request_id,
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected server errors.
    
    Returns HTTP 500 with safe generic message.
    Does not expose internal details, stack traces, or sensitive information.
    
    Args:
        request: FastAPI Request
        exc: Exception instance
        
    Returns:
        JSONResponse with generic error message
    """
    request_id = _get_request_id(request)
    
    # Log the full exception details server-side
    logger.error(
        "Unhandled exception occurred",
        exc_info=exc,
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "exception_type": type(exc).__name__,
        }
    )
    
    # Return safe generic message to client
    return _create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="An internal error occurred. Please try again later.",
        request_id=request_id,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the FastAPI application.
    
    Should be called once during application startup.
    
    Args:
        app: FastAPI application instance
    """
    # FastAPI HTTPException handler
    app.add_exception_handler(HTTPException, http_exception_handler)
    
    # Starlette HTTPException handler (for 404s on unknown routes)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    
    # Validation error handler
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    # Generic exception handler (catch-all)
    app.add_exception_handler(Exception, generic_exception_handler)
    
    logger.info("Exception handlers registered successfully")
