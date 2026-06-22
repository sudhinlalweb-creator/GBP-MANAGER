"""Stripe billing endpoints."""

from __future__ import annotations

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import OrganizationContext, get_current_organization_context, get_db
from app.schemas.billing import (
    BillingWebhookResponse,
    CheckoutRequest,
    CheckoutResponse,
    PortalRequest,
    PortalResponse,
)
from app.services.billing.stripe_service import (
    create_checkout_session,
    create_portal_session,
    handle_webhook,
)


router = APIRouter()
@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    payload: CheckoutRequest,
    context: OrganizationContext = Depends(get_current_organization_context),
    db_session: AsyncSession = Depends(get_db),
) -> CheckoutResponse:
    """Create a Stripe checkout session for the authenticated organization."""
    try:
        checkout_url = await create_checkout_session(
            context.organization,
            context.user,
            payload.plan,
            payload.success_url,
            payload.cancel_url,
            db_session,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return CheckoutResponse(checkout_url=checkout_url)


@router.post("/portal", response_model=PortalResponse)
async def create_portal(
    payload: PortalRequest,
    context: OrganizationContext = Depends(get_current_organization_context),
) -> PortalResponse:
    """Create a Stripe customer portal session for the authenticated organization."""
    if context.organization.stripe_customer_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription found",
        )

    try:
        portal_url = await create_portal_session(context.organization, payload.return_url)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return PortalResponse(portal_url=portal_url)


@router.post("/webhook", response_model=BillingWebhookResponse)
async def handle_billing_webhook(
    request: Request,
    db_session: AsyncSession = Depends(get_db),
) -> BillingWebhookResponse:
    """Verify and process a Stripe webhook event."""
    payload = await request.body()
    try:
        signature = request.headers["stripe-signature"]
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe signature header.",
        ) from exc
    try:
        await handle_webhook(payload, signature, db_session)
    except stripe.error.SignatureVerificationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Stripe webhook signature.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    return BillingWebhookResponse(received=True)
