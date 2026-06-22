"""Base interfaces and shared types for SERP data acquisition."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


class SERPClientError(Exception):
    """Base error raised for outbound SERP acquisition failures."""


class SERPBlockedError(SERPClientError):
    """Raised when the upstream search provider appears to block the request."""


class SERPParseError(Exception):
    """Raised when SERP HTML cannot be parsed into meaningful ranking data."""


@dataclass
class SERPFetchResult:
    """Raw response payload and metadata returned by a SERP client."""

    keyword: str
    html: str
    request_url: str
    status_code: int
    applied_uule: str | None = None
    applied_lat: float | None = None
    applied_lng: float | None = None
    headers: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseSERPClient(ABC):
    """Abstract interface for swappable SERP transport implementations."""

    @abstractmethod
    async def fetch_rankings(
        self,
        keyword: str,
        uule: str | None = None,
        lat: float | None = None,
        lng: float | None = None,
    ) -> SERPFetchResult:
        """Fetch the raw SERP payload for a keyword under a localization context."""
