"""Shared FastAPI dependencies for authentication and tenant scoping."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.session import get_db_session
from app.models.project import Project
from app.models.user import User
from app.organizations.models import Organization, OrganizationMembership


bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class OrganizationContext:
    """Resolved tenant scope for the authenticated request."""

    organization: Organization
    membership: OrganizationMembership
    user: User


async def get_current_user(
    db_session: AsyncSession = Depends(get_db_session),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> User:
    """Return the authenticated user extracted from the bearer token."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided.",
        )

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = UUID(payload["sub"])
    except (ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
        ) from exc

    user = await db_session.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user is inactive or missing.",
        )

    return user


async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """Return the authenticated user only when they have superuser access."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser access is required for this resource.",
        )

    return current_user


async def get_current_organization_context(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> OrganizationContext:
    """Return the first organization membership for the authenticated user."""
    statement = (
        select(OrganizationMembership, Organization)
        .join(Organization, OrganizationMembership.organization_id == Organization.id)
        .where(OrganizationMembership.user_id == current_user.id)
        .order_by(OrganizationMembership.created_at.asc())
    )
    row = (await db_session.execute(statement)).first()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The authenticated user is not assigned to an organization.",
        )

    membership, organization = row
    return OrganizationContext(
        organization=organization,
        membership=membership,
        user=current_user,
    )


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
