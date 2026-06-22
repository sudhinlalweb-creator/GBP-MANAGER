"""Provider-agnostic AI configuration surface for future audit and assistant modules."""

from __future__ import annotations

from dataclasses import dataclass

from app.core.config import get_settings


@dataclass
class AIProviderStatus:
    """Expose whether required providers are configured."""

    openai_enabled: bool
    gemini_enabled: bool


def get_ai_provider_status() -> AIProviderStatus:
    """Return AI provider readiness based on environment configuration."""
    settings = get_settings()
    return AIProviderStatus(
        openai_enabled=bool(settings.openai_api_key),
        gemini_enabled=bool(settings.google_api_key),
    )
