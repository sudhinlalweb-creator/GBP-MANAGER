"""Text normalization helpers."""

from __future__ import annotations

import re


def slugify(value: str) -> str:
    """Return a URL-safe slug from freeform text."""
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    normalized = normalized.strip("-")
    if not normalized:
        raise ValueError("Unable to derive a slug from the provided value.")
    return normalized
