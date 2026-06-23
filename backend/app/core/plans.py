"""Single source of truth for GBP Manager plan definitions and limit enforcement."""

from __future__ import annotations

from typing import TypedDict

from fastapi import HTTPException, status


class PlanSpec(TypedDict):
    subscription_tier: str
    location_limit: int
    keyword_limit: int


PLANS: dict[str, PlanSpec] = {
    "trial": PlanSpec(subscription_tier="trial", location_limit=1, keyword_limit=5),
    "starter": PlanSpec(subscription_tier="starter", location_limit=1, keyword_limit=20),
    "pro": PlanSpec(subscription_tier="pro", location_limit=5, keyword_limit=50),
    "agency": PlanSpec(subscription_tier="agency", location_limit=999, keyword_limit=999),
}

_UPGRADE_URL = "/settings/billing"


def get_plan(plan: str) -> PlanSpec:
    """Return the PlanSpec for a named plan, raising ValueError if unknown."""
    normalized = plan.strip().lower()
    if normalized not in PLANS:
        raise ValueError(f"Unsupported billing plan '{normalized}'.")
    return PLANS[normalized]


def assert_within_limit(
    resource: str,
    current: int,
    limit: int,
    plan_name: str,
) -> None:
    """Raise HTTP 402 if adding one more resource would exceed the plan limit.

    Args:
        resource: Human-readable resource name, e.g. "location" or "keyword".
        current:  Count of existing resources the org already has.
        limit:    The plan's maximum allowed count.
        plan_name: The org's current plan name (shown in the error message).
    """
    if current >= limit:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=(
                f"{resource.capitalize()} limit of {limit} reached on the {plan_name!r} plan. "
                f"Upgrade your plan at {_UPGRADE_URL} to add more."
            ),
        )
