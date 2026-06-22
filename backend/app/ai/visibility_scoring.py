"""Visibility and pillar score calculators for GBP audit reports."""

from __future__ import annotations

import math


def compute_visibility_score(
    completeness_score: int,
    review_score: int,
    engagement_score: int,
) -> int:
    """Return a composite visibility score weighted across three pillars.

    Weights: completeness 40%, reviews 40%, engagement 20%.
    """
    score = (completeness_score * 0.40) + (review_score * 0.40) + (engagement_score * 0.20)
    return max(0, min(100, round(score)))


def compute_review_score(
    review_count: int | None,
    average_rating: float | None,
) -> int:
    """Return a 0–100 score derived from review volume and average rating.

    Rating contribution (0–60): scales 1.0–5.0 linearly to 0–60.
    Count contribution (0–40): log scale capped at 100 reviews = 40 pts.
    """
    rating_pts = 0.0
    if average_rating is not None:
        clamped = max(1.0, min(5.0, float(average_rating)))
        rating_pts = ((clamped - 1.0) / 4.0) * 60.0

    count_pts = 0.0
    if review_count is not None and review_count > 0:
        count_pts = min(40.0, (math.log10(review_count + 1) / math.log10(101)) * 40.0)

    return max(0, min(100, round(rating_pts + count_pts)))


def compute_engagement_score(total_photos: int | None) -> int:
    """Return a placeholder engagement score based on photos only (Phase 3 scope).

    Posts and Q&A will increase this in Phase 5.
    """
    if total_photos is None or total_photos == 0:
        return 0
    if total_photos < 3:
        return 20
    if total_photos < 10:
        return 50
    return 80
