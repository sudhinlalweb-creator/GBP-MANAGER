"""Top-level API router for version 1 endpoints."""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    agency,
    audit,
    auth,
    automation,
    billing,
    dashboard,
    google,
    organizations,
    posts,
    projects,
    reviews,
    tracking,
)


api_router = APIRouter()
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(agency.router, prefix="/agency", tags=["agency"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(automation.router, prefix="/automation", tags=["automation"])
api_router.include_router(billing.router, prefix="/billing", tags=["billing"])
api_router.include_router(google.router, prefix="/google", tags=["google"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(posts.router, prefix="/posts", tags=["posts"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
api_router.include_router(tracking.router, prefix="/track", tags=["tracking"])
