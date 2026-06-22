"""Heuristic AI audit service with provider-ready abstraction."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.providers import get_ai_provider_status
from app.api.deps import OrganizationContext
from app.google.models import GoogleAccount, GoogleBusinessProfile
from app.models.project import Project
from app.models.ranking_history import RankingHistory
from app.schemas.audit import (
    AuditProviderStatus,
    AuditRecommendation,
    AuditSummaryResponse,
    ScoreResponse,
)


@dataclass
class AuditInputs:
    """Collected data needed to compute audit scores."""

    connected_accounts: int
    synced_profiles: int
    profiles_with_category: int
    profiles_with_website: int
    ranking_rows: int
    visible_rank_rows: int
    top_ten_rows: int
    failed_rank_rows: int


class AIAuditService:
    """Compute Phase 3 scores and recommendations for one tenant context."""

    async def build_summary(
        self,
        db_session: AsyncSession,
        context: OrganizationContext,
    ) -> AuditSummaryResponse:
        """Return an org-scoped audit summary."""
        inputs = await self._collect_inputs(db_session, context)
        last_audit_at = datetime.now(timezone.utc)

        profile_completion_score = self._clamp_score(
            15
            + min(inputs.connected_accounts, 3) * 15
            + self._safe_percentage(inputs.profiles_with_category, inputs.synced_profiles) * 25 // 100
            + self._safe_percentage(inputs.profiles_with_website, inputs.synced_profiles) * 30 // 100
            + min(inputs.synced_profiles, 5) * 3
        )

        visibility_score = self._clamp_score(
            10
            + self._safe_percentage(inputs.visible_rank_rows, inputs.ranking_rows) * 45 // 100
            + self._safe_percentage(inputs.top_ten_rows, inputs.ranking_rows) * 35 // 100
            - min(inputs.failed_rank_rows * 5, 20)
        )

        seo_score = self._clamp_score((profile_completion_score * 55 + visibility_score * 45) // 100)

        business_health_score = self._clamp_score(
            (seo_score * 50)
            // 100
            + min(inputs.connected_accounts, 2) * 10
            + min(inputs.synced_profiles, 5) * 5
            + min(inputs.ranking_rows, 10) * 2
        )

        recommendations = self._build_recommendations(inputs)
        provider_status = get_ai_provider_status()

        return AuditSummaryResponse(
            organization_id=context.organization.id,
            audit_status="completed" if inputs.connected_accounts or inputs.synced_profiles else "not_started",
            seo_score=seo_score,
            business_health_score=business_health_score,
            visibility_score=visibility_score,
            profile_completion_score=profile_completion_score,
            last_audit_at=last_audit_at,
            recommendations_count=len(recommendations),
            provider_status=AuditProviderStatus(
                openai_enabled=provider_status.openai_enabled,
                gemini_enabled=provider_status.gemini_enabled,
            ),
            recommendations=recommendations,
        )

    async def get_seo_score(
        self,
        db_session: AsyncSession,
        context: OrganizationContext,
    ) -> ScoreResponse:
        """Return the SEO score only."""
        summary = await self.build_summary(db_session, context)
        return ScoreResponse(
            organization_id=summary.organization_id,
            score_name="seo_score",
            score=summary.seo_score,
            last_audit_at=summary.last_audit_at,
        )

    async def get_business_health_score(
        self,
        db_session: AsyncSession,
        context: OrganizationContext,
    ) -> ScoreResponse:
        """Return the business health score only."""
        summary = await self.build_summary(db_session, context)
        return ScoreResponse(
            organization_id=summary.organization_id,
            score_name="business_health_score",
            score=summary.business_health_score,
            last_audit_at=summary.last_audit_at,
        )

    async def _collect_inputs(
        self,
        db_session: AsyncSession,
        context: OrganizationContext,
    ) -> AuditInputs:
        accounts = (
            (
                await db_session.execute(
                    select(GoogleAccount).where(
                        GoogleAccount.organization_id == context.organization.id,
                    )
                )
            )
            .scalars()
            .all()
        )
        profiles = (
            (
                await db_session.execute(
                    select(GoogleBusinessProfile).where(
                        GoogleBusinessProfile.organization_id == context.organization.id,
                    )
                )
            )
            .scalars()
            .all()
        )
        projects = (
            (
                await db_session.execute(
                    select(Project).where(Project.owner_id == context.user.id)
                )
            )
            .scalars()
            .all()
        )
        project_ids = [project.id for project in projects]
        ranking_rows = []
        if project_ids:
            ranking_rows = (
                (
                    await db_session.execute(
                        select(RankingHistory).where(RankingHistory.project_id.in_(project_ids))
                    )
                )
                .scalars()
                .all()
            )

        visible_rank_rows = sum(
            1 for row in ranking_rows if row.organic_rank is not None or row.map_pack_rank is not None
        )
        top_ten_rows = sum(
            1
            for row in ranking_rows
            if (row.organic_rank is not None and row.organic_rank <= 10)
            or (row.map_pack_rank is not None and row.map_pack_rank <= 3)
        )
        failed_rank_rows = sum(1 for row in ranking_rows if row.status == "failed")

        return AuditInputs(
            connected_accounts=len(accounts),
            synced_profiles=len(profiles),
            profiles_with_category=sum(1 for profile in profiles if profile.primary_category),
            profiles_with_website=sum(1 for profile in profiles if profile.website_url),
            ranking_rows=len(ranking_rows),
            visible_rank_rows=visible_rank_rows,
            top_ten_rows=top_ten_rows,
            failed_rank_rows=failed_rank_rows,
        )

    def _build_recommendations(self, inputs: AuditInputs) -> list[AuditRecommendation]:
        recommendations: list[AuditRecommendation] = []

        if inputs.connected_accounts == 0:
            recommendations.append(
                AuditRecommendation(
                    title="Connect a Google account",
                    priority="high",
                    impact_area="integration",
                    rationale="No Google Business Profile account is connected, so profile sync and audit depth are limited.",
                )
            )
        if inputs.synced_profiles == 0:
            recommendations.append(
                AuditRecommendation(
                    title="Run an initial profile sync",
                    priority="high",
                    impact_area="profile_data",
                    rationale="No Google Business Profiles have been synced into the platform yet.",
                )
            )
        if inputs.synced_profiles > 0 and inputs.profiles_with_website < inputs.synced_profiles:
            recommendations.append(
                AuditRecommendation(
                    title="Complete website links on all profiles",
                    priority="medium",
                    impact_area="profile_completion",
                    rationale="Some synced profiles are missing website URLs, which weakens profile completeness and conversion pathways.",
                )
            )
        if inputs.synced_profiles > 0 and inputs.profiles_with_category < inputs.synced_profiles:
            recommendations.append(
                AuditRecommendation(
                    title="Review primary business categories",
                    priority="medium",
                    impact_area="relevance",
                    rationale="Some synced profiles are missing a primary category, which can reduce local relevance and discovery.",
                )
            )
        if inputs.ranking_rows == 0:
            recommendations.append(
                AuditRecommendation(
                    title="Start keyword tracking",
                    priority="high",
                    impact_area="visibility",
                    rationale="No rank history exists yet, so visibility trends and drop detection are unavailable.",
                )
            )
        elif inputs.top_ten_rows == 0:
            recommendations.append(
                AuditRecommendation(
                    title="Prioritize pages targeting top commercial local keywords",
                    priority="high",
                    impact_area="rank_tracking",
                    rationale="Tracked keywords are not yet reaching top local positions, so optimization focus should shift to category and landing-page alignment.",
                )
            )
        if inputs.failed_rank_rows > 0:
            recommendations.append(
                AuditRecommendation(
                    title="Review ranking task failures",
                    priority="medium",
                    impact_area="operations",
                    rationale="Some ranking runs failed, which can distort trend accuracy and health reporting.",
                )
            )

        if not recommendations:
            recommendations.append(
                AuditRecommendation(
                    title="Maintain audit cadence",
                    priority="low",
                    impact_area="governance",
                    rationale="Profile completeness and visibility signals are healthy. Keep running regular audits and sync jobs.",
                )
            )

        return recommendations

    @staticmethod
    def _safe_percentage(numerator: int, denominator: int) -> int:
        if denominator <= 0:
            return 0
        return int((numerator / denominator) * 100)

    @staticmethod
    def _clamp_score(value: int) -> int:
        return max(0, min(100, value))
