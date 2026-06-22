"""Schemas for AI audit, SEO score, and business health responses."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AuditProviderStatus(BaseModel):
    """LLM provider readiness exposed to the API."""

    openai_enabled: bool
    gemini_enabled: bool


class AuditRecommendation(BaseModel):
    """One actionable recommendation from the audit engine."""

    title: str
    priority: str
    impact_area: str
    rationale: str


class AuditSummaryResponse(BaseModel):
    """Org-scoped audit summary used by the API and dashboard."""

    organization_id: UUID
    audit_status: str
    seo_score: int
    business_health_score: int
    visibility_score: int
    profile_completion_score: int
    last_audit_at: datetime
    recommendations_count: int
    provider_status: AuditProviderStatus
    recommendations: list[AuditRecommendation]


class ScoreResponse(BaseModel):
    """Simple numeric score response."""

    organization_id: UUID
    score_name: str
    score: int
    last_audit_at: datetime
