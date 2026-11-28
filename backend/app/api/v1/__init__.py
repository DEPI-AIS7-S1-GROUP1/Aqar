"""API v1 router.

Central router for all /api/v1 endpoints.
Individual feature routers are registered here as they are implemented.
"""

from fastapi import APIRouter

# Create the main v1 router
router = APIRouter(prefix="/api/v1")

# Future router registrations:
# When implementing new features, import and include their routers here:
#
# from app.api.v1 import auth, listings, conversations, metrics
# router.include_router(auth.router, prefix="/auth", tags=["auth"])
# router.include_router(listings.router, prefix="/listings", tags=["listings"])
# router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
# router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
