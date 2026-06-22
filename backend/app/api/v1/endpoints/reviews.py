"""GBP review management endpoints."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import OrganizationContext, get_current_organization_context
from app.db.session import get_db_session
from app.google.client import GoogleBusinessProfileClient, GoogleIntegrationError, GoogleOAuthClient
from app.google.models import GoogleAccount, GoogleBusinessProfile
from app.models.review import GBPReview
from app.schemas.review import (
    ReviewListResponse,
    ReviewReplyRequest,
    ReviewReplyResponse,
    ReviewResponse,
    ReviewSyncAcceptedResponse,
)
from app.worker.review_tasks import sync_profile_reviews


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


@router.get("/profiles/{profile_id}/reviews", response_model=ReviewListResponse)
async def list_profile_reviews(
    profile_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    rating: int | None = Query(default=None, ge=1, le=5),
    sentiment: str | None = Query(default=None),
    context: OrganizationContext = Depends(get_current_organization_context),
    db: AsyncSession = Depends(get_db_session),
) -> ReviewListResponse:
    """Return paginated reviews for a GBP profile, optionally filtered."""
    await _get_profile_for_org(db, profile_id, context.organization.id)

    query = select(GBPReview).where(GBPReview.google_profile_id == profile_id)
    if rating is not None:
        query = query.where(GBPReview.rating == rating)
    if sentiment:
        query = query.where(GBPReview.sentiment == sentiment)

    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    reviews = (
        await db.scalars(
            query.order_by(GBPReview.review_time.desc().nullslast()).offset(offset).limit(limit)
        )
    ).all()

    return ReviewListResponse(
        reviews=[ReviewResponse.model_validate(r) for r in reviews],
        total=total or 0,
    )


@router.post(
    "/profiles/{profile_id}/reviews/sync",
    response_model=ReviewSyncAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def sync_reviews(
    profile_id: UUID,
    context: OrganizationContext = Depends(get_current_organization_context),
    db: AsyncSession = Depends(get_db_session),
) -> ReviewSyncAcceptedResponse:
    """Trigger a background sync of reviews from Google for a profile."""
    await _get_profile_for_org(db, profile_id, context.organization.id)
    try:
        task = sync_profile_reviews.delay(str(profile_id))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Background worker unavailable.",
        ) from exc
    return ReviewSyncAcceptedResponse(message="Review sync queued.", task_id=task.id)


@router.post("/profiles/{profile_id}/reviews/{review_id}/reply", response_model=ReviewReplyResponse)
async def reply_to_review(
    profile_id: UUID,
    review_id: UUID,
    payload: ReviewReplyRequest,
    context: OrganizationContext = Depends(get_current_organization_context),
    db: AsyncSession = Depends(get_db_session),
) -> ReviewReplyResponse:
    """Post or update a reply to a customer review."""
    profile = await _get_profile_for_org(db, profile_id, context.organization.id)
    review = await db.scalar(
        select(GBPReview).where(
            GBPReview.id == review_id,
            GBPReview.google_profile_id == profile_id,
        )
    )
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found.")

    access_token = await _get_fresh_access_token(db, profile)
    try:
        await GoogleBusinessProfileClient().reply_to_review(
            access_token,
            profile.google_location_name,
            review.google_review_id,
            payload.reply_text,
        )
    except GoogleIntegrationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    now = datetime.now(timezone.utc)
    review.reply_text = payload.reply_text
    review.replied_at = now
    db.add(review)
    await db.commit()

    return ReviewReplyResponse(review_id=review.id, reply_text=payload.reply_text, replied_at=now)


@router.delete(
    "/profiles/{profile_id}/reviews/{review_id}/reply",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_review_reply(
    profile_id: UUID,
    review_id: UUID,
    context: OrganizationContext = Depends(get_current_organization_context),
    db: AsyncSession = Depends(get_db_session),
) -> None:
    """Delete an existing reply from a review."""
    profile = await _get_profile_for_org(db, profile_id, context.organization.id)
    review = await db.scalar(
        select(GBPReview).where(
            GBPReview.id == review_id,
            GBPReview.google_profile_id == profile_id,
        )
    )
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found.")

    access_token = await _get_fresh_access_token(db, profile)
    try:
        await GoogleBusinessProfileClient().delete_review_reply(
            access_token,
            profile.google_location_name,
            review.google_review_id,
        )
    except GoogleIntegrationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    review.reply_text = None
    review.replied_at = None
    db.add(review)
    await db.commit()
