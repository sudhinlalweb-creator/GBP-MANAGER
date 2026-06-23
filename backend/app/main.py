"""FastAPI application entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.rate_limit import limiter
from app.core.sentry import init_sentry
from app.db.session import AsyncSessionLocal


configure_logging()
init_sentry()   # no-op when SENTRY_DSN is absent
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description=(
        "Multi-tenant AI Local SEO SaaS platform backend. "
        "This API powers organizations, locations, Google Business Profile sync, "
        "AI audits, rank tracking, automation, and agency workflows."
    ),
    # Disable interactive docs in production — full API surface should not be public
    docs_url=None if settings.environment == "production" else "/docs",
    redoc_url=None if settings.environment == "production" else "/redoc",
)

# Rate limiting — must be set before routes are processed
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_origin_regex=settings.cors_allow_origin_regex,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
)
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/", tags=["root"])
async def root() -> dict[str, object]:
    """Workspace root endpoint for health and discovery."""
    return {
        "name": settings.app_name,
        "api_prefix": settings.api_v1_prefix,
        "status": "running",
    }


@app.get("/health", tags=["health"])
async def healthcheck() -> dict[str, str]:
    """Container health endpoint — probes the database connection."""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "ok", "db": "ok"}
    except Exception:
        # Return 503 so load balancers stop routing traffic to an unhealthy instance
        from fastapi import Response
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=503,
            content={"status": "degraded", "db": "unreachable"},
        )
