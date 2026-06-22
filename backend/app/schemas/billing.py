"""Stripe billing API schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class CheckoutRequest(BaseModel):
    """Create a Stripe Checkout session for a plan change."""

    plan: Literal["starter", "pro", "agency"]
    success_url: str = Field(..., min_length=1, max_length=2048)
    cancel_url: str = Field(..., min_length=1, max_length=2048)


class CheckoutResponse(BaseModel):
    """Stripe Checkout session response."""

    checkout_url: str


class PortalRequest(BaseModel):
    """Create a Stripe billing portal session."""

    return_url: str = Field(..., min_length=1, max_length=2048)


class PortalResponse(BaseModel):
    """Stripe billing portal redirect."""

    portal_url: str


class BillingWebhookResponse(BaseModel):
    """Acknowledgement for Stripe webhooks."""

    received: bool
