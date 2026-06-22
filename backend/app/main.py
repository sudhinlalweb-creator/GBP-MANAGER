"""FastAPI application entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging


configure_logging()
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description=(
        "Multi-tenant AI Local SEO SaaS platform backend. "
        "This API powers organizations, locations, Google Business Profile sync, "
        "AI audits, rank tracking, automation, and agency workflows."
    ),
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_origin_regex=settings.cors_allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/", tags=["root"])
async def root() -> dict[str, object]:
    """Workspace root endpoint for health and discovery."""
    return {
        "name": settings.app_name,
        "docs_url": "/docs",
        "api_prefix": settings.api_v1_prefix,
        "status": "running",
    }


@app.get("/health", tags=["health"])
async def healthcheck() -> dict[str, str]:
    """Container health endpoint."""
    return {"status": "ok"}
