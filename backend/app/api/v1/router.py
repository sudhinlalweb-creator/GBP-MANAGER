"""Top-level API router for version 1 endpoints."""

from fastapi import APIRouter

from app.api.v1.endpoints import admin, audit, auth, dashboard, google, projects, tracking


api_router = APIRouter()
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(google.router, prefix="/google", tags=["google"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(tracking.router, prefix="/track", tags=["tracking"])
