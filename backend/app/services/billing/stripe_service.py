"""Stripe billing service layer."""

from __future__ import annotations

import asyncio
from typing import Any

import stripe
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.organizations.models import Organization
from app.worker.celery_app import celery_app


settings = get_settings()
PLAN_LIMITS = {
    "trial": {"location_limit": 1, "keyword_limit": 5, "subscription_tier": "trial"},
    "starter": {"location_limit": 1, "keyword_limit": 20, "subscription_tier": "starter"},
    "pro": {"location_limit": 5, "keyword_limit": 50, "subscription_tier": "pro"},
    "agency": {"location_limit": 999, "keyword_limit": 999, "subscription_tier": "agency"},
}


def _configure_stripe() -> None:
    """Configure the Stripe SDK from environment settings."""
    if not settings.stripe_secret_key:
        raise ValueError("Stripe billing is not configured.")
    stripe.api_key = settings.stripe_secret_key


async def _run_stripe(callable_obj: Any, /, *args: Any, **kwargs: Any) -> Any:
    """Run the synchronous Stripe SDK without blocking the event loop."""
    return await asyncio.to_thread(callable_obj, *args, **kwargs)


def _resolve_price_id(plan: str) -> str:
    """Return the configured Stripe price ID for a paid plan."""
    normalized_plan = plan.strip().lower()
    price_id_map = {
        "starter": settings.stripe_price_id_starter,
        "pro": settings.stripe_price_id_pro,
        "agency": settings.stripe_price_id_agency,
    }
    price_id = price_id_map.get(normalized_plan)
    if not price_id:
        raise ValueError(f"Stripe price ID is not configured for plan '{normalized_plan}'.")
    return price_id


def _apply_plan_to_org(organization: Organization, plan: str) -> None:
    """Apply plan-derived limits and tier fields to an organization."""
    normalized_plan = plan.strip().lower()
    if normalized_plan not in PLAN_LIMITS:
        raise ValueError(f"Unsupported billing plan '{normalized_plan}'.")

    limits = PLAN_LIMITS[normalized_plan]
    organization.plan = normalized_plan
    organization.subscription_tier = str(limits["subscription_tier"])
    organization.location_limit = int(limits["location_limit"])
    organization.keyword_limit = int(limits["keyword_limit"])


async def get_or_create_stripe_customer(org: Organization, user: Any, db: AsyncSession) -> str:
    """Return an existing Stripe customer ID or create one and persist it."""
    _configure_stripe()
    if org.stripe_customer_id:
        return org.stripe_customer_id

    customer = await _run_stripe(
        stripe.Customer.create,
        email=user.email,
        name=org.name,
        metadata={"org_id": str(org.id)},
    )
    customer_id = str(customer["id"])
    org.stripe_customer_id = customer_id
    db.add(org)
    await db.commit()
    await db.refresh(org)
    return customer_id


async def create_checkout_session(
    org: Organization,
    user: Any,
    plan: str,
    success_url: str,
    cancel_url: str,
    db: AsyncSession,
) -> str:
    """Create a Stripe Checkout session and return the hosted URL."""
    normalized_plan = plan.strip().lower()
    if normalized_plan not in PLAN_LIMITS or normalized_plan == "trial":
        raise ValueError("Plan must be one of starter, pro, or agency.")

    _configure_stripe()
    customer_id = await get_or_create_stripe_customer(org, user, db)
    price_id = _resolve_price_id(normalized_plan)
    session = await _run_stripe(
        stripe.checkout.Session.create,
        customer=customer_id,
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"org_id": str(org.id), "plan": normalized_plan},
    )
    session_url = session.get("url")
    if not session_url:
        raise ValueError("Stripe did not return a checkout URL.")
    return str(session_url)


async def create_portal_session(org: Organization, return_url: str) -> str:
    """Create a Stripe billing portal session and return its URL."""
    _configure_stripe()
    if not org.stripe_customer_id:
        raise ValueError("No active subscription found")

    session = await _run_stripe(
        stripe.billing_portal.Session.create,
        customer=org.stripe_customer_id,
        return_url=return_url,
    )
    portal_url = session.get("url")
    if not portal_url:
        raise ValueError("Stripe did not return a portal URL.")
    return str(portal_url)


async def handle_webhook(payload: bytes, sig_header: str, db: AsyncSession) -> None:
    """Verify and dispatch a Stripe webhook event."""
    _configure_stripe()
    if not settings.stripe_webhook_secret:
        raise ValueError("Stripe webhook verification is not configured.")

    event = await _run_stripe(
        stripe.Webhook.construct_event,
        payload=payload,
        sig_header=sig_header,
        secret=settings.stripe_webhook_secret,
    )

    event_type = str(event["type"])
    event_object = dict(event["data"]["object"])
    if event_type == "checkout.session.completed":
        await _on_checkout_completed(event_object, db)
    elif event_type == "invoice.payment_succeeded":
        await _on_payment_succeeded(event_object, db)
    elif event_type == "invoice.payment_failed":
        await _on_payment_failed(event_object, db)
    elif event_type == "customer.subscription.deleted":
        await _on_subscription_deleted(event_object, db)


async def _on_checkout_completed(session: dict[str, Any], db: AsyncSession) -> None:
    """Persist organization billing state after successful checkout."""
    metadata = session.get("metadata") or {}
    org_id = metadata.get("org_id")
    plan = str(metadata.get("plan") or "").strip().lower()
    if not org_id or plan not in PLAN_LIMITS:
        return

    organization = await db.get(Organization, org_id)
    if organization is None:
        return

    organization.stripe_customer_id = session.get("customer") or organization.stripe_customer_id
    organization.stripe_subscription_id = (
        session.get("subscription") or organization.stripe_subscription_id
    )
    organization.subscription_status = "active"
    _apply_plan_to_org(organization, plan)
    db.add(organization)
    await db.commit()


async def _on_payment_succeeded(invoice: dict[str, Any], db: AsyncSession) -> None:
    """Mark an organization subscription as active after a successful invoice."""
    customer_id = invoice.get("customer")
    if not customer_id:
        return

    organization = await db.scalar(
        select(Organization).where(Organization.stripe_customer_id == str(customer_id))
    )
    if organization is None:
        return

    organization.subscription_status = "active"
    db.add(organization)
    await db.commit()


async def _on_payment_failed(invoice: dict[str, Any], db: AsyncSession) -> None:
    """Mark an organization subscription as past due and queue an alert."""
    customer_id = invoice.get("customer")
    if not customer_id:
        return

    organization = await db.scalar(
        select(Organization).where(Organization.stripe_customer_id == str(customer_id))
    )
    if organization is None:
        return

    organization.subscription_status = "past_due"
    db.add(organization)
    await db.commit()
    celery_app.send_task(
        "app.worker.tasks.send_billing_alert_email",
        kwargs={
            "org_id": str(organization.id),
            "reason": "invoice.payment_failed",
        },
    )


async def _on_subscription_deleted(subscription: dict[str, Any], db: AsyncSession) -> None:
    """Reset an organization back to the trial plan after cancellation."""
    subscription_id = subscription.get("id")
    customer_id = subscription.get("customer")
    organization = None
    if subscription_id:
        organization = await db.scalar(
            select(Organization).where(Organization.stripe_subscription_id == str(subscription_id))
        )
    if organization is None and customer_id:
        organization = await db.scalar(
            select(Organization).where(Organization.stripe_customer_id == str(customer_id))
        )
    if organization is None:
        return

    _apply_plan_to_org(organization, "trial")
    organization.subscription_status = "canceled"
    organization.stripe_subscription_id = None
    db.add(organization)
    await db.commit()
