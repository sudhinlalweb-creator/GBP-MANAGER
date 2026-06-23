"""Authentication endpoints."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from redis import asyncio as redis_asyncio
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.organizations.models import Organization, OrganizationMembership
from app.schemas.auth import (
    AuthenticatedUserResponse,
    ForgotPasswordRequest,
    LogoutRequest,
    MessageResponse,
    OrganizationMembershipResponse,
    RefreshTokenRequest,
    ResetPasswordRequest,
    TokenResponse,
    UpdateMeRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.core.rate_limit import limiter
from app.utils.text import slugify
from app.worker.celery_app import celery_app


router = APIRouter()
settings = get_settings()
reset_password_serializer = URLSafeTimedSerializer(settings.secret_key, salt="password-reset")
redis_client = redis_asyncio.from_url(
    settings.celery_broker_url,
    encoding="utf-8",
    decode_responses=True,
)
PASSWORD_RESET_TOKEN_MAX_AGE_SECONDS = 3600
PASSWORD_RESET_TASK_NAME = "app.worker.tasks.send_password_reset_email"


async def _get_memberships(
    db_session: AsyncSession,
    user_id: UUID,
) -> list[OrganizationMembershipResponse]:
    """Return organization memberships for a user."""
    rows = await db_session.execute(
        select(OrganizationMembership, Organization)
        .join(Organization, OrganizationMembership.organization_id == Organization.id)
        .where(OrganizationMembership.user_id == user_id)
        .order_by(OrganizationMembership.created_at.asc())
    )
    memberships: list[OrganizationMembershipResponse] = []
    for membership, organization in rows.all():
        memberships.append(
            OrganizationMembershipResponse(
                organization_id=organization.id,
                organization_name=organization.name,
                organization_slug=organization.slug,
                subscription_tier=organization.subscription_tier,
                role=membership.role,
                joined_at=membership.created_at,
            )
        )
    return memberships


async def _serialize_authenticated_user(
    db_session: AsyncSession,
    user: User,
) -> AuthenticatedUserResponse:
    """Return the authenticated user response payload with memberships."""
    user_payload = UserResponse.model_validate(user).model_dump()
    return AuthenticatedUserResponse(
        **user_payload,
        memberships=await _get_memberships(db_session, user.id),
    )


def _build_token_response(
    *,
    access_token: str,
    refresh_token: str,
    user: AuthenticatedUserResponse,
) -> TokenResponse:
    """Construct the standard token response payload."""
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user,
    )


async def _claim_pending_organization_invites(
    db_session: AsyncSession,
    *,
    user: User,
) -> None:
    """Attach any pending organization invites that match the new user's email."""
    pending_memberships = (
        await db_session.scalars(
            select(OrganizationMembership).where(
                func.lower(OrganizationMembership.invitation_email) == user.email.lower(),
                OrganizationMembership.is_pending.is_(True),
            )
        )
    ).all()

    for membership in pending_memberships:
        membership.user_id = user.id
        membership.is_pending = False
        db_session.add(membership)


async def _ensure_refresh_token_is_active(refresh_token: str) -> dict[str, object]:
    """Validate a refresh token and ensure it has not been blocklisted."""
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required.",
        )

    if await redis_client.exists(f"blocklist:{refresh_token}"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked.",
        )

    return payload


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("3/minute")
async def register_user(
    request: Request,
    payload: UserRegisterRequest,
    db_session: AsyncSession = Depends(get_db),
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
        plan="trial",
        subscription_tier="trial",
        location_limit=1,
        keyword_limit=5,
        billing_email=email,
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
    await _claim_pending_organization_invites(db_session, user=user)
    await db_session.commit()
    await db_session.refresh(user)

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    return _build_token_response(
        access_token=access_token,
        refresh_token=refresh_token,
        user=await _serialize_authenticated_user(db_session, user),
    )


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login_user(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db_session: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticate a user and return a JWT access token."""
    email = form_data.username.strip().lower()
    user = await db_session.scalar(select(User).where(func.lower(User.email) == email))
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The user account is inactive.",
        )

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    return _build_token_response(
        access_token=access_token,
        refresh_token=refresh_token,
        user=await _serialize_authenticated_user(db_session, user),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    payload: RefreshTokenRequest,
    db_session: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Issue a fresh token pair from a valid refresh token."""
    token_payload = await _ensure_refresh_token_is_active(payload.refresh_token)
    user = await db_session.get(User, UUID(str(token_payload["sub"])))
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user is inactive or missing.",
        )

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    return _build_token_response(
        access_token=access_token,
        refresh_token=refresh_token,
        user=await _serialize_authenticated_user(db_session, user),
    )


@router.post("/logout", response_model=MessageResponse)
async def logout_user(payload: LogoutRequest) -> MessageResponse:
    """Revoke the supplied refresh token by writing it to the Redis blocklist."""
    token_payload = await _ensure_refresh_token_is_active(payload.refresh_token)
    expires_at = int(token_payload["exp"])
    ttl_seconds = max(expires_at - int(datetime.now(timezone.utc).timestamp()), 1)
    await redis_client.set(f"blocklist:{payload.refresh_token}", "1", ex=ttl_seconds)
    return MessageResponse(message="Logged out successfully.")


@router.post("/forgot-password", response_model=MessageResponse)
@limiter.limit("3/minute")
async def forgot_password(
    request: Request,
    payload: ForgotPasswordRequest,
    db_session: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Generate a reset token and enqueue a background email task when the user exists."""
    email = payload.email.strip().lower()
    user = await db_session.scalar(select(User).where(func.lower(User.email) == email))
    if user is not None and user.is_active:
        reset_token = reset_password_serializer.dumps({"sub": str(user.id)})
        celery_app.send_task(
            PASSWORD_RESET_TASK_NAME,
            kwargs={"email": user.email, "reset_token": reset_token},
        )

    return MessageResponse(
        message="If the account exists, a password reset email has been queued."
    )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    payload: ResetPasswordRequest,
    db_session: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Validate the signed reset token and store the new password hash."""
    try:
        token_payload = reset_password_serializer.loads(
            payload.token,
            max_age=PASSWORD_RESET_TOKEN_MAX_AGE_SECONDS,
        )
    except SignatureExpired as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset token has expired.",
        ) from exc
    except BadSignature as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset token is invalid.",
        ) from exc

    user = await db_session.get(User, UUID(str(token_payload["sub"])))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User was not found.",
        )

    user.hashed_password = hash_password(payload.new_password)
    db_session.add(user)
    await db_session.commit()
    return MessageResponse(message="Password has been reset successfully.")


@router.get("/me", response_model=AuthenticatedUserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db),
) -> AuthenticatedUserResponse:
    """Return the authenticated user profile with organization memberships."""
    return await _serialize_authenticated_user(db_session, current_user)


@router.patch("/me", response_model=AuthenticatedUserResponse)
async def update_me(
    payload: UpdateMeRequest,
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db),
) -> AuthenticatedUserResponse:
    """Update the authenticated user's display name."""
    current_user.full_name = payload.full_name.strip() if payload.full_name else None
    db_session.add(current_user)
    await db_session.commit()
    await db_session.refresh(current_user)
    return await _serialize_authenticated_user(db_session, current_user)
