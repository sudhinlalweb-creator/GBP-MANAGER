"""Scoring helpers for Google Business Profile completeness."""

from __future__ import annotations

from app.google.models import GoogleBusinessProfile


def compute_completeness_score(profile: GoogleBusinessProfile) -> int:
    """Return a weighted completeness score for a synced Google Business Profile."""
    score = 0

    if profile.google_location_name and profile.google_location_name.strip():
        score += 10
    if profile.primary_category and profile.primary_category.strip():
        score += 15
    if profile.phone_number and profile.phone_number.strip():
        score += 10
    if (
        profile.address_street
        and profile.address_street.strip()
        and profile.address_city
        and profile.address_city.strip()
        and profile.address_country_code
        and profile.address_country_code.strip()
    ):
        score += 10
    if profile.website_url and profile.website_url.strip():
        score += 10
    if profile.is_verified:
        score += 15
    if profile.review_count is not None and profile.review_count >= 5:
        score += 10
    if profile.average_rating is not None and profile.average_rating >= 4.0:
        score += 10
    if profile.total_photos is not None and profile.total_photos >= 3:
        score += 10

    return max(0, min(100, int(score)))
