"""GBP local post management endpoints."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import OrganizationContext, get_current_organization_context, require_plan
from app.db.session import get_db_session
from app.google.client import GoogleBusinessProfileClient, GoogleIntegrationError, GoogleOAuthClient
from app.google.models import GoogleAccount, GoogleBusinessProfile
from app.models.post import GBPPost
from app.schemas.post import PostCreateRequest, PostListResponse, PostResponse


logger = logging.getLogger(__name__)
router = APIRouter()


async def _get_profile_for_org(
    db: AsyncSession,
    profile_id: UUID,
    org_id: UUID,
) -> GoogleBusinessProfile:
    profile = await db.scalar(
        select(GoogleBusinessProfile).where(
            GoogleBusinessProfile.id == profile_id,
            GoogleBusinessProfile.organization_id == org_id,
        )
    )
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")
    return profile


async def _get_fresh_access_token(db: AsyncSession, profile: GoogleBusinessProfile) -> str:
    account = await db.get(GoogleAccount, profile.google_account_id)
    if account is None or not account.refresh_token_encrypted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google account is not connected.",
        )
    try:
        tokens = await GoogleOAuthClient().refresh_access_token(account.refresh_token_encrypted)
        return tokens["access_token"]
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to refresh Google access token.",
        ) from exc


@router.get("/profiles/{profile_id}/posts", response_model=PostListResponse)
async def list_profile_posts(
    profile_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    state: str | None = Query(default=None),
    context: OrganizationContext = Depends(get_current_organization_context),
    db: AsyncSession = Depends(get_db_session),
) -> PostListResponse:
    """Return paginated posts for a GBP profile."""
    await _get_profile_for_org(db, profile_id, context.organization.id)

    query = select(GBPPost).where(GBPPost.google_profile_id == profile_id)
    if state:
        query = query.where(GBPPost.state == state)

    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    posts = (
        await db.scalars(query.order_by(GBPPost.created_at.desc()).offset(offset).limit(limit))
    ).all()

    return PostListResponse(
        posts=[PostResponse.model_validate(p) for p in posts],
        total=total or 0,
    )


@router.post(
    "/profiles/{profile_id}/posts",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_plan("starter"))],
)
async def create_profile_post(
    profile_id: UUID,
    payload: PostCreateRequest,
    context: OrganizationContext = Depends(get_current_organization_context),
    db: AsyncSession = Depends(get_db_session),
) -> PostResponse:
    """Create and optionally publish a GBP local post (starter plan required)."""
    profile = await _get_profile_for_org(db, profile_id, context.organization.id)

    if payload.scheduled_at and payload.scheduled_at > datetime.now(timezone.utc):
        # Save as scheduled — the beat job will publish it
        post = GBPPost(
            google_profile_id=profile_id,
            post_type=payload.post_type,
            summary=payload.summary,
            call_to_action_type=payload.call_to_action_type,
            call_to_action_url=payload.call_to_action_url,
            media_url=payload.media_url,
            scheduled_at=payload.scheduled_at,
            state="scheduled",
        )
        db.add(post)
        await db.commit()
        await db.refresh(post)
        return PostResponse.model_validate(post)

    # Publish immediately
    access_token = await _get_fresh_access_token(db, profile)
    post_data: dict = {"summary": payload.summary, "topicType": payload.post_type}
    if payload.call_to_action_type and payload.call_to_action_url:
        post_data["callToAction"] = {
            "actionType": payload.call_to_action_type,
            "url": payload.call_to_action_url,
        }
    if payload.media_url:
        post_data["media"] = [{"mediaFormat": "PHOTO", "sourceUrl": payload.media_url}]

    try:
        result = await GoogleBusinessProfileClient().create_post(
            access_token, profile.google_location_name, post_data
        )
    except GoogleIntegrationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    post = GBPPost(
        google_profile_id=profile_id,
        google_post_id=result.get("name", "").split("/")[-1],
        post_type=payload.post_type,
        summary=payload.summary,
        call_to_action_type=payload.call_to_action_type,
        call_to_action_url=payload.call_to_action_url,
        media_url=payload.media_url,
        state="published",
        published_at=datetime.now(timezone.utc),
        raw_data=result,
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return PostResponse.model_validate(post)


@router.delete(
    "/profiles/{profile_id}/posts/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_profile_post(
    profile_id: UUID,
    post_id: UUID,
    context: OrganizationContext = Depends(get_current_organization_context),
    db: AsyncSession = Depends(get_db_session),
) -> Response:
    """Delete a GBP local post (removes from Google and marks deleted locally)."""
    profile = await _get_profile_for_org(db, profile_id, context.organization.id)
    post = await db.scalar(
        select(GBPPost).where(
            GBPPost.id == post_id,
            GBPPost.google_profile_id == profile_id,
        )
    )
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")

    if post.state == "published" and post.google_post_id:
        access_token = await _get_fresh_access_token(db, profile)
        try:
            await GoogleBusinessProfileClient().delete_post(
                access_token, profile.google_location_name, post.google_post_id
            )
        except GoogleIntegrationError as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    post.state = "deleted"
    db.add(post)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
