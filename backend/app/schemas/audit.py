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
    """One actionable recommendation from the heuristic audit engine."""

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


# ── Phase 3: per-profile AI audit report schemas ──────────────────────────────

class AuditRecommendationSchema(BaseModel):
    """One AI-generated recommendation stored inside an AuditReport."""

    id: str
    priority: str
    category: str
    title: str
    detail: str
    impact_score: int
    is_auto_fixable: bool
    suggested_value: str | None = None
    field_path: str | None = None


class AuditScoreResponse(BaseModel):
    """Per-report score breakdown response."""

    report_id: UUID
    visibility_score: int | None
    completeness_score: int | None
    review_score: int | None
    engagement_score: int | None
    score_breakdown: dict


class AuditReportSummaryResponse(BaseModel):
    """Lightweight audit report response without recommendations payload."""

    id: UUID
    organization_id: UUID
    google_profile_id: UUID
    status: str
    visibility_score: int | None
    completeness_score: int | None
    review_score: int | None
    engagement_score: int | None
    ai_provider: str | None
    ai_model: str | None
    started_at: datetime | None
    completed_at: datetime | None
    error_reason: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditReportResponse(AuditReportSummaryResponse):
    """Full audit report response including AI recommendations."""

    recommendations: list[AuditRecommendationSchema] = []
    raw_ai_response: dict | None = None

    model_config = {"from_attributes": True}


class AuditReportListResponse(BaseModel):
    """Paginated audit report list."""

    reports: list[AuditReportSummaryResponse]
    total: int
