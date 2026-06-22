"""Read-only admin service layer for platform operations."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Iterable
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.google.models import GoogleBusinessProfile
from app.models.heatmap_run import HeatmapRun
from app.models.ranking_history import RankingHistory
from app.models.user import User
from app.organizations.models import Organization, OrganizationMembership
from app.schemas.admin import (
    AdminDashboardResponse,
    AdminOrganizationItem,
    AdminOrganizationTierUpdateRequest,
    AdminOverviewResponse,
    AdminQueueHealthItem,
    AdminServiceHealthItem,
    AdminSubscriptionItem,
    AdminSystemHealthResponse,
    AdminUserItem,
    AdminUserStatusUpdateRequest,
)


_PLAN_MRR = {
    "starter": 99.0,
    "growth": 299.0,
    "pro": 499.0,
    "agency": 899.0,
    "agency growth": 899.0,
    "multi-location pro": 499.0,
    "enterprise": 1999.0,
}

_ALLOWED_SUBSCRIPTION_TIERS = {
    "starter",
    "growth",
    "pro",
    "agency",
    "agency growth",
    "multi-location pro",
    "enterprise",
}


class AdminService:
    """Aggregate platform-wide data for the admin panel."""

    async def get_dashboard(self, db_session: AsyncSession) -> AdminDashboardResponse:
        """Return the full read-only admin dashboard payload."""
        overview = await self._build_overview(db_session)
        users = await self._build_users(db_session)
        organizations = await self._build_organizations(db_session)
        subscriptions = await self._build_subscriptions(db_session)
        system_health = await self._build_system_health(db_session)

        return AdminDashboardResponse(
            overview=overview,
            users=users,
            organizations=organizations,
            subscriptions=subscriptions,
            system_health=system_health,
        )

    async def update_user_status(
        self,
        db_session: AsyncSession,
        *,
        actor: User,
        user_id: UUID,
        payload: AdminUserStatusUpdateRequest,
    ) -> AdminUserItem:
        """Activate or suspend one user."""
        user = await db_session.get(User, user_id)
        if user is None:
            raise ValueError("User was not found.")

        if actor.id == user.id and not payload.is_active:
            raise PermissionError("You cannot suspend your own superuser account.")

        user.is_active = payload.is_active
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        memberships_by_user = await _load_memberships_by_user(db_session, [user.id])
        membership = memberships_by_user.get(user.id)
        return _serialize_admin_user(user, membership)

    async def update_organization_tier(
        self,
        db_session: AsyncSession,
        *,
        organization_id: UUID,
        payload: AdminOrganizationTierUpdateRequest,
    ) -> AdminOrganizationItem:
        """Update one organization's subscription tier."""
        normalized_tier = payload.subscription_tier.strip().lower()
        if normalized_tier not in _ALLOWED_SUBSCRIPTION_TIERS:
            raise ValueError("Unsupported subscription tier.")

        organization = await db_session.get(Organization, organization_id)
        if organization is None:
            raise ValueError("Organization was not found.")

        organization.subscription_tier = normalized_tier
        db_session.add(organization)
        await db_session.commit()
        await db_session.refresh(organization)

        member_counts = await _count_members_by_organization(db_session, [organization.id])
        location_counts = await _count_locations_by_organization(db_session, [organization.id])
        return _serialize_admin_organization(
            organization,
            members_count=member_counts.get(organization.id, 0),
            locations_count=location_counts.get(organization.id, 0),
        )

    async def _build_overview(self, db_session: AsyncSession) -> AdminOverviewResponse:
        active_users = int(
            await db_session.scalar(select(func.count(User.id)).where(User.is_active.is_(True))) or 0
        )
        organizations = int(await db_session.scalar(select(func.count(Organization.id))) or 0)

        tier_counts = (
            await db_session.execute(
                select(Organization.subscription_tier, func.count(Organization.id))
                .group_by(Organization.subscription_tier)
            )
        ).all()
        estimated_mrr = round(
            sum(_monthly_revenue_for_tier(tier) * count for tier, count in tier_counts),
            2,
        )

        failed_heatmaps = int(
            await db_session.scalar(
                select(func.count(HeatmapRun.id)).where(HeatmapRun.status == "failed")
            )
            or 0
        )
        failed_rankings = int(
            await db_session.scalar(
                select(func.count(RankingHistory.id)).where(RankingHistory.status == "failed")
            )
            or 0
        )
        incident_status = (
            "Investigate recent task failures"
            if failed_heatmaps + failed_rankings > 0
            else "No active incidents detected"
        )

        return AdminOverviewResponse(
            active_users=active_users,
            organizations=organizations,
            monthly_recurring_revenue=estimated_mrr,
            incident_status=incident_status,
        )

    async def _build_users(self, db_session: AsyncSession) -> list[AdminUserItem]:
        users = (
            await db_session.scalars(select(User).order_by(User.updated_at.desc()).limit(20))
        ).all()
        memberships_by_user = await _load_memberships_by_user(db_session, [user.id for user in users])

        items: list[AdminUserItem] = []
        for user in users:
            membership = memberships_by_user.get(user.id)
            items.append(_serialize_admin_user(user, membership))
        return items

    async def _build_organizations(self, db_session: AsyncSession) -> list[AdminOrganizationItem]:
        organizations = (
            await db_session.scalars(
                select(Organization).order_by(Organization.updated_at.desc()).limit(12)
            )
        ).all()
        organization_ids = [organization.id for organization in organizations]
        member_counts = await _count_members_by_organization(db_session, organization_ids)
        location_counts = await _count_locations_by_organization(db_session, organization_ids)

        items: list[AdminOrganizationItem] = []
        for organization in organizations:
            items.append(
                _serialize_admin_organization(
                    organization,
                    members_count=member_counts.get(organization.id, 0),
                    locations_count=location_counts.get(organization.id, 0),
                )
            )
        return items

    async def _build_subscriptions(self, db_session: AsyncSession) -> list[AdminSubscriptionItem]:
        rows = (
            await db_session.execute(
                select(
                    Organization.subscription_tier,
                    func.count(Organization.id),
                    func.count(OrganizationMembership.id),
                )
                .outerjoin(
                    OrganizationMembership,
                    OrganizationMembership.organization_id == Organization.id,
                )
                .group_by(Organization.subscription_tier)
                .order_by(func.count(Organization.id).desc())
            )
        ).all()

        return [
            AdminSubscriptionItem(
                tier=tier,
                tenants_count=int(tenants_count or 0),
                members_count=int(members_count or 0),
                estimated_monthly_revenue=round(_monthly_revenue_for_tier(tier) * int(tenants_count or 0), 2),
                status=_resolve_subscription_status(tier),
            )
            for tier, tenants_count, members_count in rows
        ]

    async def _build_system_health(self, db_session: AsyncSession) -> AdminSystemHealthResponse:
        settings = get_settings()
        db_ok = await _database_is_healthy(db_session)
        services = [
            AdminServiceHealthItem(
                name="FastAPI API",
                status="healthy",
                detail="Versioned admin, product, and auth routes are mounted.",
                metric=f"prefix {settings.api_v1_prefix}",
            ),
            AdminServiceHealthItem(
                name="PostgreSQL",
                status="healthy" if db_ok else "offline",
                detail="Primary application datastore connectivity check.",
                metric="select 1 ok" if db_ok else "connection failed",
            ),
            AdminServiceHealthItem(
                name="Redis / Celery",
                status="healthy" if bool(settings.celery_broker_url) else "offline",
                detail="Background task broker and result backend configuration.",
                metric=settings.celery_default_queue,
            ),
            AdminServiceHealthItem(
                name="AI Providers",
                status="healthy" if (settings.openai_api_key or settings.google_api_key) else "degraded",
                detail="LLM provider readiness for AI audits and assistant features.",
                metric=_ai_provider_metric(settings.openai_api_key, settings.google_api_key),
            ),
        ]

        now = datetime.now(timezone.utc)
        window_start = now - timedelta(hours=24)
        queues = [
            await _build_ranking_queue_health(db_session, window_start),
            await _build_heatmap_queue_health(db_session, window_start),
        ]

        return AdminSystemHealthResponse(services=services, queues=queues)


class _MembershipSummary:
    """Primary membership summary attached to a user."""

    def __init__(self, role: str, organization_name: str) -> None:
        self.role = role
        self.organization_name = organization_name


def _serialize_admin_user(
    user: User,
    membership: _MembershipSummary | None,
) -> AdminUserItem:
    role = "superuser" if user.is_superuser else (membership.role if membership else "member")
    organization_name = membership.organization_name if membership else None
    status = _resolve_user_status(user)
    return AdminUserItem(
        id=user.id,
        name=user.full_name,
        email=user.email,
        role=role,
        organization=organization_name,
        status=status,
        is_active=user.is_active,
        last_active_at=user.updated_at,
    )


def _serialize_admin_organization(
    organization: Organization,
    *,
    members_count: int,
    locations_count: int,
) -> AdminOrganizationItem:
    status = _resolve_organization_status(organization.subscription_tier, members_count)
    return AdminOrganizationItem(
        id=organization.id,
        name=organization.name,
        subscription_tier=organization.subscription_tier,
        locations_count=locations_count,
        members_count=members_count,
        status=status,
        renewal_date=None,
    )


def _monthly_revenue_for_tier(tier: str | None) -> float:
    normalized = (tier or "starter").strip().lower()
    return _PLAN_MRR.get(normalized, 199.0)


def _resolve_user_status(user: User) -> str:
    if not user.is_active:
        return "suspended"
    if user.subscription_status == "trial":
        return "trial"
    return "active"


def _resolve_organization_status(subscription_tier: str, members_count: int) -> str:
    normalized_tier = subscription_tier.strip().lower()
    if normalized_tier == "starter":
        return "trial" if members_count <= 1 else "healthy"
    if normalized_tier in {"agency", "agency growth", "enterprise"}:
        return "healthy"
    return "attention"


def _resolve_subscription_status(tier: str) -> str:
    normalized_tier = tier.strip().lower()
    if normalized_tier in {"starter", "growth"}:
        return "expansion"
    if normalized_tier in {"agency", "agency growth", "enterprise"}:
        return "stable"
    return "monitor"


def _ai_provider_metric(openai_api_key: str | None, google_api_key: str | None) -> str:
    enabled = []
    if openai_api_key:
        enabled.append("OpenAI")
    if google_api_key:
        enabled.append("Gemini")
    return ", ".join(enabled) if enabled else "no provider keys"


async def _database_is_healthy(db_session: AsyncSession) -> bool:
    try:
        await db_session.execute(select(1))
    except Exception:
        return False
    return True


async def _load_memberships_by_user(
    db_session: AsyncSession,
    user_ids: Iterable[UUID],
) -> dict[UUID, _MembershipSummary]:
    user_ids = list(user_ids)
    if not user_ids:
        return {}

    rows = (
        await db_session.execute(
            select(
                OrganizationMembership.user_id,
                OrganizationMembership.role,
                Organization.name,
            )
            .join(Organization, Organization.id == OrganizationMembership.organization_id)
            .where(OrganizationMembership.user_id.in_(user_ids))
            .order_by(OrganizationMembership.created_at.asc())
        )
    ).all()

    memberships: dict[UUID, _MembershipSummary] = {}
    for user_id, role, organization_name in rows:
        memberships.setdefault(user_id, _MembershipSummary(role=role, organization_name=organization_name))
    return memberships


async def _count_members_by_organization(
    db_session: AsyncSession,
    organization_ids: list[UUID],
) -> dict[UUID, int]:
    if not organization_ids:
        return {}

    rows = (
        await db_session.execute(
            select(
                OrganizationMembership.organization_id,
                func.count(OrganizationMembership.id),
            )
            .where(OrganizationMembership.organization_id.in_(organization_ids))
            .group_by(OrganizationMembership.organization_id)
        )
    ).all()
    return {organization_id: int(count) for organization_id, count in rows}


async def _count_locations_by_organization(
    db_session: AsyncSession,
    organization_ids: list[UUID],
) -> dict[UUID, int]:
    if not organization_ids:
        return {}

    rows = (
        await db_session.execute(
            select(
                GoogleBusinessProfile.organization_id,
                func.count(GoogleBusinessProfile.id),
            )
            .where(GoogleBusinessProfile.organization_id.in_(organization_ids))
            .group_by(GoogleBusinessProfile.organization_id)
        )
    ).all()
    return {organization_id: int(count) for organization_id, count in rows}


async def _build_ranking_queue_health(
    db_session: AsyncSession,
    window_start: datetime,
) -> AdminQueueHealthItem:
    waiting = int(
        await db_session.scalar(
            select(func.count(RankingHistory.id)).where(RankingHistory.status.in_(["pending", "queued"]))
        )
        or 0
    )
    running = int(
        await db_session.scalar(
            select(func.count(RankingHistory.id)).where(RankingHistory.status == "running")
        )
        or 0
    )
    failed_24h = int(
        await db_session.scalar(
            select(func.count(RankingHistory.id)).where(
                RankingHistory.status == "failed",
                RankingHistory.started_at >= window_start,
            )
        )
        or 0
    )
    return AdminQueueHealthItem(
        queue_name="rank-tracking",
        waiting=waiting,
        running=running,
        failed_24h=failed_24h,
    )


async def _build_heatmap_queue_health(
    db_session: AsyncSession,
    window_start: datetime,
) -> AdminQueueHealthItem:
    waiting = int(
        await db_session.scalar(
            select(func.count(HeatmapRun.id)).where(HeatmapRun.status.in_(["pending", "queued"]))
        )
        or 0
    )
    running = int(
        await db_session.scalar(
            select(func.count(HeatmapRun.id)).where(HeatmapRun.status == "running")
        )
        or 0
    )
    failed_24h = int(
        await db_session.scalar(
            select(func.count(HeatmapRun.id)).where(
                HeatmapRun.status == "failed",
                HeatmapRun.started_at >= window_start,
            )
        )
        or 0
    )
    return AdminQueueHealthItem(
        queue_name="heatmaps",
        waiting=waiting,
        running=running,
        failed_24h=failed_24h,
    )
