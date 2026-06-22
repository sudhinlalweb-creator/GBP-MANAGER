"""Authentication endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db_session
from app.models.user import User
from app.organizations.models import Organization, OrganizationMembership
from app.schemas.auth import TokenResponse, UserLoginRequest, UserRegisterRequest, UserResponse
from app.utils.text import slugify


router = APIRouter()


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    payload: UserRegisterRequest,
    db_session: AsyncSession = Depends(get_db_session),
) -> TokenResponse:
    """Register a new user and immediately issue an access token."""
    email = payload.email.strip().lower()
    existing_users_count = await db_session.scalar(select(func.count(User.id)))
    existing_user = await db_session.scalar(
        select(User).where(func.lower(User.email) == email)
    )
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    user = User(
        email=email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name.strip() if payload.full_name else None,
        is_superuser=(existing_users_count or 0) == 0,
    )
    db_session.add(user)
    await db_session.flush()

    organization_name = (
        f"{payload.full_name.strip()} Workspace"
        if payload.full_name and payload.full_name.strip()
        else f"{email.split('@', maxsplit=1)[0]} Workspace"
    )
    organization = Organization(
        name=organization_name,
        slug=f"{slugify(organization_name)}-{str(user.id)[:8]}",
    )
    db_session.add(organization)
    await db_session.flush()

    membership = OrganizationMembership(
        organization_id=organization.id,
        user_id=user.id,
        role="owner",
        invitation_email=email,
    )
    db_session.add(membership)
    await db_session.commit()
    await db_session.refresh(user)

    access_token = create_access_token(str(user.id))
    return TokenResponse(access_token=access_token, user=UserResponse.model_validate(user))


@router.post("/login", response_model=TokenResponse)
async def login_user(
    payload: UserLoginRequest,
    db_session: AsyncSession = Depends(get_db_session),
) -> TokenResponse:
    """Authenticate a user and return a JWT access token."""
    email = payload.email.strip().lower()
    user = await db_session.scalar(select(User).where(func.lower(User.email) == email))
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    access_token = create_access_token(str(user.id))
    return TokenResponse(access_token=access_token, user=UserResponse.model_validate(user))


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Return the authenticated user profile."""
    return UserResponse.model_validate(current_user)
