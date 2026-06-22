"""HTTP-based Google SERP client with proxy and anti-bot hooks."""

from __future__ import annotations

from typing import Any

import httpx

from app.core.config import get_settings
from app.services.serp.base import BaseSERPClient, SERPBlockedError, SERPClientError, SERPFetchResult


class HTTPGoogleSERPClient(BaseSERPClient):
    """Fetch Google SERP HTML over HTTP while keeping transport details modular."""

    def __init__(self) -> None:
        self.settings = get_settings()

    async def fetch_rankings(
        self,
        keyword: str,
        uule: str | None = None,
        lat: float | None = None,
        lng: float | None = None,
    ) -> SERPFetchResult:
        """Return raw Google SERP HTML for the provided keyword and geo context."""
        query = keyword.strip()
        if not query:
            raise ValueError("Keyword is required to fetch rankings.")

        headers = self._build_headers()
        params = self._build_query_params(keyword=query, uule=uule, lat=lat, lng=lng)
        timeout = httpx.Timeout(self.settings.serp_request_timeout_seconds)

        try:
            async with self._build_client(timeout=timeout, headers=headers) as client:
                response = await client.get(
                    self.settings.google_base_url,
                    params=params,
                    follow_redirects=True,
                )
        except httpx.TimeoutException as exc:
            raise SERPClientError(f"SERP request timed out for keyword '{query}'.") from exc
        except httpx.HTTPError as exc:
            raise SERPClientError(f"SERP request failed for keyword '{query}': {exc}") from exc

        if response.status_code in {403, 429, 503} or self._response_looks_blocked(response.text):
            raise SERPBlockedError(
                f"Google blocked the request for keyword '{query}' with status "
                f"{response.status_code}."
            )

        if response.status_code >= 400:
            raise SERPClientError(
                f"Unexpected SERP response status {response.status_code} for keyword '{query}'."
            )

        return SERPFetchResult(
            keyword=query,
            html=response.text,
            request_url=str(response.url),
            status_code=response.status_code,
            applied_uule=uule,
            applied_lat=lat,
            applied_lng=lng,
            headers=dict(response.headers),
            metadata={"query_params": params},
        )

    def _build_client(
        self,
        timeout: httpx.Timeout,
        headers: dict[str, str],
    ) -> httpx.AsyncClient:
        """Build an async HTTP client, optionally routing requests through a proxy."""
        proxy_url = self._pick_proxy_url()
        transport = httpx.AsyncHTTPTransport(proxy=proxy_url) if proxy_url else None
        return httpx.AsyncClient(
            timeout=timeout,
            headers=headers,
            transport=transport,
        )

    def _pick_proxy_url(self) -> str | None:
        """Return the next proxy endpoint to use for the request."""
        proxies = self.settings.serp_proxies
        return proxies.get("https://") or proxies.get("http://")

    def _build_headers(self) -> dict[str, str]:
        """Return a realistic browser-like header set."""
        return {
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/avif,image/webp,image/apng,*/*;q=0.8"
            ),
            "Accept-Language": f"{self.settings.serp_default_language}-{self.settings.serp_default_country},"
            f"{self.settings.serp_default_language};q=0.9",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": self.settings.serp_user_agent,
        }

    def _build_query_params(
        self,
        keyword: str,
        uule: str | None,
        lat: float | None,
        lng: float | None,
    ) -> dict[str, Any]:
        """Construct a querystring for localized Google SERP retrieval."""
        params: dict[str, Any] = {
            "q": keyword,
            "hl": self.settings.serp_default_language,
            "gl": self.settings.serp_default_country,
            "num": 10,
            "pws": 0,
        }
        if uule:
            params["uule"] = uule
        if lat is not None and lng is not None:
            # Google does not document a stable lat/lng query contract for web SERP,
            # so keep the coordinate injection isolated here for future browser/API swaps.
            params["near"] = f"{lat},{lng}"
            params["latlng"] = f"{lat},{lng},13z"
        return params

    @staticmethod
    def _response_looks_blocked(html: str) -> bool:
        """Return True when the HTML resembles an anti-bot or captcha response."""
        normalized_html = html.lower()
        block_markers = (
            "our systems have detected unusual traffic",
            "sorry...",
            "/sorry/",
            "detected unusual traffic from your computer network",
            "captcha",
        )
        return any(marker in normalized_html for marker in block_markers)
