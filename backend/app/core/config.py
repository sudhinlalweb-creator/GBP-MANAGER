"""Application configuration loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


class Settings(BaseSettings):
    """Strongly typed application settings."""

    environment: str = "development"
    app_name: str = "AI Local SEO Platform API"
    api_v1_prefix: str = "/api/v1"
    frontend_url: str | None = Field(default=None, alias="FRONTEND_URL")
    secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "local_seo"
    postgres_user: str = "local_seo"
    postgres_password: str
    database_echo: bool = False
    database_url_override: str | None = Field(default=None, alias="DATABASE_URL")
    alembic_database_url_override: str | None = Field(default=None, alias="ALEMBIC_DATABASE_URL")

    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0

    celery_default_queue: str = "local-seo"
    google_base_url: str = "https://www.google.com/search"
    serp_request_timeout_seconds: float = 30.0
    serp_default_language: str = "en"
    serp_default_country: str = "us"
    serp_http_proxy_url: str | None = None
    serp_https_proxy_url: str | None = None
    google_client_id: str | None = None
    google_client_secret: str | None = None
    google_redirect_uri: str | None = None
    google_maps_api_key: str | None = None
    stripe_secret_key: str | None = None
    stripe_webhook_secret: str | None = None
    stripe_price_id_starter: str | None = None
    stripe_price_id_pro: str | None = None
    stripe_price_id_agency: str | None = None
    openai_api_key: str | None = None
    google_api_key: str | None = None
    sentry_dsn: str | None = None
    cors_allow_origins_raw: str = Field(
        default=(
            "http://localhost:3000,"
            "http://127.0.0.1:3000,"
            "http://localhost:8080,"
            "http://127.0.0.1:8080"
        ),
        alias="CORS_ALLOW_ORIGINS",
    )
    cors_allow_origin_regex: str | None = Field(default=None, alias="CORS_ALLOW_ORIGIN_REGEX")
    serp_user_agent: str = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        populate_by_name=True,
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url(self) -> str:
        """SQLAlchemy async database DSN."""
        if self.database_url_override:
            return self._normalize_async_database_url(self.database_url_override)

        return (
            "postgresql+asyncpg://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def alembic_database_url(self) -> str:
        """Database DSN used by Alembic migrations."""
        if self.alembic_database_url_override:
            return self._normalize_async_database_url(self.alembic_database_url_override)

        if self.database_url_override:
            return self._normalize_async_database_url(self.database_url_override)

        return self.database_url

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_connect_args(self) -> dict[str, str]:
        """Extra SQLAlchemy connect args derived from hosted Postgres URLs."""
        if not self.database_url_override:
            return {}
        return self._extract_database_connect_args(self.database_url_override)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def alembic_database_connect_args(self) -> dict[str, str]:
        """Extra Alembic connect args derived from hosted Postgres URLs."""
        source = self.alembic_database_url_override or self.database_url_override
        if not source:
            return {}
        return self._extract_database_connect_args(source)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def celery_broker_url(self) -> str:
        """Redis broker DSN used by Celery."""
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def celery_result_backend(self) -> str:
        """Redis backend DSN used by Celery task results."""
        return self.celery_broker_url

    @computed_field  # type: ignore[prop-decorator]
    @property
    def serp_proxies(self) -> dict[str, str]:
        """Normalized proxy configuration for outbound SERP requests."""
        proxies: dict[str, str] = {}
        if self.serp_http_proxy_url:
            proxies["http://"] = self.serp_http_proxy_url
        if self.serp_https_proxy_url:
            proxies["https://"] = self.serp_https_proxy_url
        return proxies

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cors_allow_origins(self) -> list[str]:
        """Normalized list of explicit CORS origins."""
        return [
            origin.strip()
            for origin in self.cors_allow_origins_raw.split(",")
            if origin.strip()
        ]

    @staticmethod
    def _normalize_async_database_url(value: str) -> str:
        """Normalize Postgres DSNs for async SQLAlchemy engines and Neon SSL settings."""
        url = make_url(value)
        drivername = url.drivername
        if drivername in {"postgres", "postgresql"}:
            drivername = "postgresql+asyncpg"
        elif drivername == "postgresql+psycopg":
            drivername = "postgresql+asyncpg"

        query = dict(url.query)
        query.pop("sslmode", None)
        query.pop("ssl", None)
        query.pop("channel_binding", None)

        normalized_url = url.set(drivername=drivername, query=query)
        return normalized_url.render_as_string(hide_password=False)

    @staticmethod
    def _extract_database_connect_args(value: str) -> dict[str, str]:
        """Translate raw Postgres URL parameters into asyncpg-compatible connect args."""
        url = make_url(value)
        connect_args: dict[str, str] = {}
        if url.query.get("sslmode") == "require":
            connect_args["ssl"] = "require"
        return connect_args


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings object for process-wide reuse."""
    return Settings()
