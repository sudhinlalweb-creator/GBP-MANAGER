"""Shared FastAPI dependencies for authentication and tenant scoping."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.session import get_db_session
from app.models.project import Project
from app.models.user import User
from app.organizations.models import Organization, OrganizationMembership


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
PLAN_ORDER = {"trial": 0, "starter": 1, "pro": 2, "agency": 3}


@dataclass
class OrganizationContext:
    """Resolved tenant scope for the authenticated request."""

    organization: Organization
    membership: OrganizationMembership
    user: User


async def get_db():
    """Yield an async database session for request-scoped dependencies."""
    async for session in get_db_session():
        yield session


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Return the authenticated user extracted from the bearer token."""
    try:
        payload = decode_token(token)
        user_id = UUID(payload["sub"])
    except (KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await db.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user is inactive or missing.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """Return the authenticated user only when they have superuser access."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser access is required for this resource.",
        )

    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_active_superuser),
) -> User:
    """Backward-compatible alias for the admin endpoints."""
    return current_user


async def get_current_organization_context(
    org_id: UUID | None = None,
    db_session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OrganizationContext:
    """Return the requested organization membership or fall back to the first tenant."""
    statement = (
        select(OrganizationMembership, Organization)
        .join(Organization, OrganizationMembership.organization_id == Organization.id)
        .where(OrganizationMembership.user_id == current_user.id)
    )
    if org_id is not None:
        statement = statement.where(OrganizationMembership.organization_id == org_id)

    statement = statement.order_by(OrganizationMembership.created_at.asc())
    row = (await db_session.execute(statement)).first()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if org_id is not None else status.HTTP_403_FORBIDDEN,
            detail=(
                "Organization was not found."
                if org_id is not None
                else "The authenticated user is not assigned to an organization."
            ),
        )

    membership, organization = row
    return OrganizationContext(
        organization=organization,
        membership=membership,
        user=current_user,
    )


def require_plan(min_plan: str):
    """Return a dependency that enforces a minimum tenant subscription tier."""
    normalized_min_plan = min_plan.strip().lower()
    if normalized_min_plan not in PLAN_ORDER:
        raise ValueError(f"Unsupported plan requirement '{min_plan}'.")

    async def _require_plan(
        context: OrganizationContext = Depends(get_current_organization_context),
    ) -> OrganizationContext:
        current_plan = context.organization.subscription_tier.strip().lower()
        if PLAN_ORDER.get(current_plan, -1) < PLAN_ORDER[normalized_min_plan]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"The '{normalized_min_plan}' plan or higher is required "
                    "for this resource."
                ),
            )
        return context

    return _require_plan


async def get_owned_project_or_404(
    project_id: UUID,
    current_user: User,
    db_session: AsyncSession,
) -> Project:
    """Return a project only when it belongs to the authenticated user."""
    statement = select(Project).where(
        Project.id == project_id,
        Project.owner_id == current_user.id,
    )
    project = await db_session.scalar(statement)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project was not found.",
        )
    return project
