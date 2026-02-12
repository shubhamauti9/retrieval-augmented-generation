"""
Routers module.
"""

from routers.ingest import router as ingest_router
from routers.query import router as query_router
from routers.admin import router as admin_router

__all__ = ["ingest_router", "query_router", "admin_router"]
