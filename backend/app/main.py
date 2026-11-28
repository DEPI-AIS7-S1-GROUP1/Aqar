"""FastAPI entry point.

S0-T2-1 only adds /health so the compose healthcheck has something to call.
Real routes (e.g. /conversations in S1-T8-2) go under app/api/v1.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import router as api_v1_router
from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.core.middleware import RequestTrackingMiddleware

app = FastAPI(title="AqarAI API")

# Register exception handlers first (before middleware)
register_exception_handlers(app)

# Configure CORS middleware
# Must be added before other middleware to work correctly
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Register request tracking middleware
app.add_middleware(RequestTrackingMiddleware)

# Include versioned API router
app.include_router(api_v1_router)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness check. Does not touch db or redis."""
    return {"status": "ok"}
