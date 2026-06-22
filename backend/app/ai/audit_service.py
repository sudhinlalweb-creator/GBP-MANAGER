"""AI audit service for GBP location audit reports."""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timedelta, timezone
from uuid import UUID

import httpx
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.audit_prompts import build_audit_system_prompt, build_audit_user_prompt
from app.ai.visibility_scoring import (
    compute_engagement_score,
    compute_review_score,
    compute_visibility_score,
)
from app.core.config import get_settings
from app.google.models import GoogleBusinessProfile
from app.google.scoring import compute_completeness_score
from app.models.audit import AuditReport


logger = logging.getLogger(__name__)
settings = get_settings()

_REQUIRED_REC_KEYS = {"priority", "category", "title", "detail"}
_AUDIT_COOLDOWN_MINUTES = 60


class AuditService:
    """Orchestrate AI GBP audit creation, execution, and retrieval."""

    async def run_audit(
        self,
        db: AsyncSession,
        organization_id: UUID,
        google_profile_id: UUID,
        requested_by_user_id: UUID,
    ) -> AuditReport:
        """Create an AuditReport, run AI analysis, and persist results."""
        profile = await self._load_profile(db, organization_id, google_profile_id)

        await self._enforce_cooldown(db, google_profile_id)

        report = AuditReport(
            organization_id=organization_id,
            google_profile_id=google_profile_id,
            requested_by_user_id=requested_by_user_id,
            status="pending",
        )
        db.add(report)
        await db.flush()

        report.status = "running"
        report.started_at = datetime.now(timezone.utc)
        db.add(report)
        await db.commit()
        await db.refresh(report)

        try:
            completeness = compute_completeness_score(profile)
            review_score = compute_review_score(profile.review_count, profile.average_rating)
            engagement_score = compute_engagement_score(profile.total_photos)
            visibility_score = compute_visibility_score(completeness, review_score, engagement_score)

            snapshot = _build_profile_snapshot(
                profile=profile,
                completeness_score=completeness,
                visibility_score=visibility_score,
            )

            provider, model, raw_response, recommendations = await _call_ai(snapshot)

            report.completeness_score = completeness
            report.review_score = review_score
            report.engagement_score = engagement_score
            report.visibility_score = visibility_score
            report.ai_provider = provider
            report.ai_model = model
            report.raw_ai_response = {"response_text": raw_response}
            report.recommendations = recommendations
            report.status = "completed"
            report.completed_at = datetime.now(timezone.utc)

        except Exception as exc:
            logger.exception(
                "Audit failed for profile_id=%s report_id=%s", google_profile_id, report.id
            )
            report.status = "failed"
            report.error_reason = str(exc)
            report.completed_at = datetime.now(timezone.utc)

        db.add(report)
        await db.commit()
        await db.refresh(report)
        return report

    async def get_report(
        self,
        db: AsyncSession,
        organization_id: UUID,
        report_id: UUID,
    ) -> AuditReport:
        """Return one audit report scoped to the organization."""
        report = await db.scalar(
            select(AuditReport).where(
                AuditReport.id == report_id,
                AuditReport.organization_id == organization_id,
            )
        )
        if report is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit report was not found.",
            )
        return report

    async def list_reports(
        self,
        db: AsyncSession,
        organization_id: UUID,
        google_profile_id: UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[AuditReport], int]:
        """Return paginated audit reports for the organization."""
        base_where = [AuditReport.organization_id == organization_id]
        if google_profile_id is not None:
            base_where.append(AuditReport.google_profile_id == google_profile_id)

        total = int(
            await db.scalar(
                select(func.count(AuditReport.id)).where(*base_where)
            )
            or 0
        )
        reports = (
            (
                await db.execute(
                    select(AuditReport)
                    .where(*base_where)
                    .order_by(AuditReport.created_at.desc())
                    .limit(limit)
                    .offset(offset)
                )
            )
            .scalars()
            .all()
        )
        return list(reports), total

    async def _load_profile(
        self,
        db: AsyncSession,
        organization_id: UUID,
        google_profile_id: UUID,
    ) -> GoogleBusinessProfile:
        profile = await db.scalar(
            select(GoogleBusinessProfile).where(
                GoogleBusinessProfile.id == google_profile_id,
                GoogleBusinessProfile.organization_id == organization_id,
            )
        )
        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Google Business Profile was not found.",
            )
        return profile

    async def _enforce_cooldown(
        self,
        db: AsyncSession,
        google_profile_id: UUID,
    ) -> None:
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=_AUDIT_COOLDOWN_MINUTES)
        recent = await db.scalar(
            select(AuditReport).where(
                AuditReport.google_profile_id == google_profile_id,
                AuditReport.status.in_(["pending", "running", "completed"]),
                AuditReport.created_at >= cutoff,
            )
        )
        if recent is not None:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="An audit was already run for this profile within the last hour.",
            )


def _build_profile_snapshot(
    profile: GoogleBusinessProfile,
    completeness_score: int,
    visibility_score: int,
) -> dict:
    """Build the profile snapshot dict sent to the AI model."""
    address_parts = [
        profile.address_street,
        profile.address_city,
        profile.address_state,
        profile.address_postal_code,
        profile.address_country_code,
    ]
    address_formatted = ", ".join(p for p in address_parts if p) or None

    return {
        "business_name": profile.google_location_name,
        "primary_category": profile.primary_category,
        "phone_number": profile.phone_number,
        "website_url": profile.website_url,
        "address": address_formatted,
        "maps_url": profile.maps_url,
        "is_verified": profile.is_verified,
        "is_suspended": profile.is_suspended,
        "review_count": profile.review_count,
        "average_rating": profile.average_rating,
        "total_photos": profile.total_photos,
        "completeness_score": completeness_score,
        "visibility_score": visibility_score,
        "missing_fields": [
            field
            for field, value in {
                "primary_category": profile.primary_category,
                "phone_number": profile.phone_number,
                "website_url": profile.website_url,
                "address": address_formatted,
            }.items()
            if not value
        ],
    }


async def _call_ai(
    snapshot: dict,
) -> tuple[str, str, str, list[dict]]:
    """Call the configured AI provider and return (provider, model, raw_text, recommendations)."""
    system_prompt = build_audit_system_prompt()
    user_prompt = build_audit_user_prompt(snapshot)

    if settings.openai_api_key:
        return await _call_openai(system_prompt, user_prompt)
    if settings.google_api_key:
        return await _call_gemini(system_prompt, user_prompt)

    raise ValueError(
        "AI provider is not configured. Set OPENAI_API_KEY or GOOGLE_API_KEY."
    )


async def _call_openai(
    system_prompt: str,
    user_prompt: str,
) -> tuple[str, str, str, list[dict]]:
    """Call OpenAI chat completions and parse the JSON response."""
    model = "gpt-4o"
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": model,
        "temperature": 0.3,
        "max_tokens": 2000,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    raw_text = await _http_post_json(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        body=body,
        extract=lambda r: r["choices"][0]["message"]["content"],
    )
    recommendations = _parse_recommendations(raw_text, system_prompt)
    return "openai", model, raw_text, recommendations


async def _call_gemini(
    system_prompt: str,
    user_prompt: str,
) -> tuple[str, str, str, list[dict]]:
    """Call Gemini generateContent and parse the JSON response."""
    model = "gemini-1.5-flash"
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}"
        f":generateContent?key={settings.google_api_key}"
    )
    body = {
        "contents": [
            {"role": "user", "parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]}
        ],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 2000},
    }
    raw_text = await _http_post_json(
        url,
        headers={"Content-Type": "application/json"},
        body=body,
        extract=lambda r: r["candidates"][0]["content"]["parts"][0]["text"],
    )
    recommendations = _parse_recommendations(raw_text, system_prompt)
    return "gemini", model, raw_text, recommendations


async def _http_post_json(
    url: str,
    headers: dict,
    body: dict,
    extract,
) -> str:
    """POST JSON to an LLM endpoint and return the extracted text content."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, headers=headers, json=body)
        response.raise_for_status()
    return extract(response.json())


def _parse_recommendations(raw_text: str, system_prompt: str) -> list[dict]:
    """Parse and validate the AI response JSON into a list of recommendation dicts."""
    try:
        parsed = json.loads(raw_text.strip())
        recs = parsed.get("recommendations", [])
    except (json.JSONDecodeError, AttributeError):
        recs = _retry_parse(raw_text)

    validated = []
    for rec in recs:
        if not isinstance(rec, dict):
            continue
        if not _REQUIRED_REC_KEYS.issubset(rec.keys()):
            continue
        if "id" not in rec:
            rec["id"] = str(uuid.uuid4())
        rec.setdefault("impact_score", 5)
        rec.setdefault("is_auto_fixable", False)
        rec.setdefault("suggested_value", None)
        rec.setdefault("field_path", None)
        validated.append(rec)

    return validated


def _retry_parse(raw_text: str) -> list[dict]:
    """Try to extract JSON from a response that may contain markdown fences."""
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        inner = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
        try:
            return json.loads(inner).get("recommendations", [])
        except (json.JSONDecodeError, AttributeError):
            pass
    raise ValueError("AI returned an unparseable response after retry.")
