"""Organization membership and invite endpoints."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    OrganizationContext,
    get_current_organization_context,
    get_current_user,
    get_db,
)
from app.core.config import get_settings
from app.core.plans import PLANS
from app.models.user import User
from app.organizations.models import Organization, OrganizationMembership
from app.schemas.auth import MessageResponse
from app.schemas.organization import (
    InviteRequest,
    MemberResponse,
    OrganizationResponse,
    OrganizationUpdateRequest,
)
from app.utils.text import slugify
from app.worker.celery_app import celery_app


router = APIRouter()
ADMIN_ROLES = {"owner", "admin"}
INVITE_ROLE_CHOICES = {"admin", "manager", "viewer"}
settings = get_settings()
invite_serializer = URLSafeTimedSerializer(settings.secret_key, salt="org-invite")

def _require_organization_admin(context: OrganizationContext) -> None:
    """Require an organization membership role with management access."""
    if context.membership.role.strip().lower() not in ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization admin access is required.",
        )


def _require_organization_owner(context: OrganizationContext) -> None:
    """Require owner access for destructive membership operations."""
    if context.membership.role.strip().lower() != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization owner access is required.",
        )


async def _count_owners(db_session: AsyncSession, organization_id: UUID) -> int:
    """Count current owner memberships for one organization."""
    return int(
        await db_session.scalar(
            select(func.count(OrganizationMembership.id)).where(
                OrganizationMembership.organization_id == organization_id,
                OrganizationMembership.role == "owner",
            )
        )
        or 0
    )


def _serialize_organization(organization: Organization) -> OrganizationResponse:
    """Convert an organization row into the API response contract."""
    plan = organization.plan.strip().lower()
    spec = PLANS.get(plan, PLANS["trial"])
    return OrganizationResponse(
        id=organization.id,
        name=organization.name,
        slug=organization.slug,
        plan=plan,
        subscription_tier=organization.subscription_tier,
        subscription_status=organization.subscription_status,
        location_limit=organization.location_limit if organization.location_limit is not None else spec["location_limit"],
        keyword_limit=organization.keyword_limit if organization.keyword_limit is not None else spec["keyword_limit"],
        trial_ends_at=organization.trial_ends_at,
        created_at=organization.created_at,
    )


def _serialize_member(membership: OrganizationMembership, user: User | None) -> MemberResponse:
    """Convert one membership row into the API response contract."""
    return MemberResponse(
        user_id=membership.user_id,
        email=user.email if user is not None else membership.invitation_email,
        full_name=user.full_name if user is not None else None,
        role=membership.role,
        is_pending=membership.is_pending,
        joined_at=membership.created_at,
    )


@router.get("", response_model=list[OrganizationResponse])
async def list_organizations(
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db),
) -> list[OrganizationResponse]:
    """Return all organizations the authenticated user belongs to."""
    rows = await db_session.execute(
        select(Organization)
        .join(OrganizationMembership, OrganizationMembership.organization_id == Organization.id)
        .where(OrganizationMembership.user_id == current_user.id)
        .order_by(Organization.created_at.asc())
    )
    return [_serialize_organization(organization) for organization in rows.scalars().all()]


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    context: OrganizationContext = Depends(get_current_organization_context),
) -> OrganizationResponse:
    """Return one organization when the user belongs to it."""
    return _serialize_organization(context.organization)


@router.patch("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    payload: OrganizationUpdateRequest,
    context: OrganizationContext = Depends(get_current_organization_context),
    db_session: AsyncSession = Depends(get_db),
) -> OrganizationResponse:
    """Update name and slug for one organization."""
    _require_organization_admin(context)
    organization = context.organization

    if payload.name is not None:
        organization.name = payload.name.strip()

    if payload.slug is not None:
        slug = slugify(payload.slug)
        existing = await db_session.scalar(
            select(Organization).where(
                Organization.slug == slug,
                Organization.id != organization.id,
            )
        )
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An organization with this slug already exists.",
            )
        organization.slug = slug

    db_session.add(organization)
    await db_session.commit()
    await db_session.refresh(organization)
    return _serialize_organization(organization)


@router.get("/{org_id}/members", response_model=list[MemberResponse])
async def list_organization_members(
    context: OrganizationContext = Depends(get_current_organization_context),
    db_session: AsyncSession = Depends(get_db),
) -> list[MemberResponse]:
    """Return all active and pending members for one organization."""
    rows = await db_session.execute(
        select(OrganizationMembership, User)
        .outerjoin(User, User.id == OrganizationMembership.user_id)
        .where(OrganizationMembership.organization_id == context.organization.id)
        .order_by(OrganizationMembership.created_at.asc())
    )
    return [_serialize_member(membership, user) for membership, user in rows.all()]


@router.post("/{org_id}/invite", response_model=MessageResponse)
async def invite_organization_member(
    payload: InviteRequest,
    context: OrganizationContext = Depends(get_current_organization_context),
    db_session: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Invite a member into an organization or attach an existing user directly."""
    _require_organization_admin(context)
    normalized_email = payload.email.strip().lower()
    normalized_role = payload.role.strip().lower()
    if normalized_role not in INVITE_ROLE_CHOICES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Role must be one of admin, manager, or viewer.",
        )

    user = await db_session.scalar(select(User).where(func.lower(User.email) == normalized_email))

    existing_membership_predicate = OrganizationMembership.invitation_email == normalized_email
    if user is not None:
        existing_membership_predicate = or_(
            OrganizationMembership.invitation_email == normalized_email,
            OrganizationMembership.user_id == user.id,
        )

    existing_membership = await db_session.scalar(
        select(OrganizationMembership).where(
            OrganizationMembership.organization_id == context.organization.id,
            existing_membership_predicate,
        )
    )
    if existing_membership is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This user is already a member or has a pending invite.",
        )

    membership = OrganizationMembership(
        organization_id=context.organization.id,
        user_id=user.id if user is not None else None,
        role=normalized_role,
        invitation_email=normalized_email,
        is_pending=user is None,
        invited_at=datetime.now(timezone.utc) if user is None else None,
    )
    db_session.add(membership)
    await db_session.commit()
    if user is None:
        invite_token = invite_serializer.dumps(
            {
                "org_id": str(context.organization.id),
                "email": normalized_email,
                "role": normalized_role,
            }
        )
        celery_app.send_task(
            "app.worker.tasks.send_org_invite_email",
            kwargs={
                "email": normalized_email,
                "invite_token": invite_token,
                "org_name": context.organization.name,
            },
        )

    return MessageResponse(message="Organization invite processed successfully.")


@router.post("/accept-invite/{token}", response_model=MessageResponse)
async def accept_organization_invite(
    token: str,
    db_session: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Accept an organization invite when the token is valid."""
    try:
        payload = invite_serializer.loads(token, max_age=72 * 60 * 60)
    except SignatureExpired as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization invite token has expired.",
        ) from exc
    except BadSignature as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization invite token is invalid.",
        ) from exc

    invite_email = str(payload.get("email", "")).strip().lower()
    organization_id = payload.get("org_id")
    invite_role = str(payload.get("role", "")).strip().lower()
    if not invite_email or not organization_id or invite_role not in INVITE_ROLE_CHOICES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization invite token is invalid.",
        )

    membership = await db_session.scalar(
        select(OrganizationMembership).where(
            OrganizationMembership.organization_id == UUID(str(organization_id)),
            OrganizationMembership.invitation_email == invite_email,
        )
    )
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization invite record was not found.",
        )

    user = await db_session.scalar(select(User).where(func.lower(User.email) == invite_email))
    if user is None:
        return MessageResponse(
            message=f"Please register with {invite_email} to complete acceptance"
        )

    membership.user_id = user.id
    membership.role = invite_role
    membership.is_pending = False
    db_session.add(membership)
    await db_session.commit()
    return MessageResponse(message="Organization invite accepted successfully.")


@router.delete("/{org_id}/members/{user_id}", response_model=MessageResponse)
async def remove_organization_member(
    user_id: UUID,
    context: OrganizationContext = Depends(get_current_organization_context),
    db_session: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Remove one active organization member."""
    _require_organization_owner(context)
    membership = await db_session.scalar(
        select(OrganizationMembership).where(
            OrganizationMembership.user_id == user_id,
            OrganizationMembership.organization_id == context.organization.id,
        )
    )
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization membership was not found.",
        )

    if membership.user_id == context.user.id and membership.role == "owner":
        owners_count = await _count_owners(db_session, context.organization.id)
        if owners_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot remove yourself as the only owner.",
            )

    await db_session.delete(membership)
    await db_session.commit()
    return MessageResponse(message="Organization member removed successfully.")
