"""Helpers for generating Google geo-localization parameters."""

from __future__ import annotations

import base64


_UULE_KEY = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
_UULE_PREFIX = "w+CAIQICI"


def build_google_uule(location_name: str) -> str:
    """Return a URL-safe Google UULE token for a canonical location string."""
    canonical_location = location_name.strip()
    if not canonical_location:
        raise ValueError("Location name is required to build a Google UULE value.")

    location_bytes = canonical_location.encode("utf-8")
    location_length = len(location_bytes)
    if location_length >= len(_UULE_KEY):
        raise ValueError("Location name is too long to encode into a Google UULE value.")

    encoded_location = base64.urlsafe_b64encode(location_bytes).decode("ascii").rstrip("=")
    return f"{_UULE_PREFIX}{_UULE_KEY[location_length]}{encoded_location}"
