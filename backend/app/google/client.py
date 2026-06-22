"""HTTP clients for Google OAuth and Google Business Profile APIs."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

import httpx

from app.core.config import get_settings


class GoogleIntegrationError(Exception):
    """Raised when a Google integration call cannot complete successfully."""


class GoogleOAuthClient:
    """OAuth client for Google account connection flows."""

    authorization_base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    token_url = "https://oauth2.googleapis.com/token"
    user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"

    def __init__(self) -> None:
        self.settings = get_settings()

    def build_authorization_url(self, state: str) -> str:
        """Return the Google OAuth URL for the configured client."""
        self._ensure_oauth_configured()
        params = {
            "client_id": self.settings.google_client_id,
            "redirect_uri": self.settings.google_redirect_uri,
            "response_type": "code",
            "scope": " ".join(
                [
                    "openid",
                    "email",
                    "profile",
                    "https://www.googleapis.com/auth/business.manage",
                ]
            ),
            "access_type": "offline",
            "include_granted_scopes": "true",
            "prompt": "consent",
            "state": state,
        }
        return f"{self.authorization_base_url}?{urlencode(params)}"

    async def exchange_code_for_tokens(self, code: str) -> dict[str, Any]:
        """Exchange an authorization code for Google OAuth tokens."""
        self._ensure_oauth_configured()
        payload = {
            "code": code,
            "client_id": self.settings.google_client_id,
            "client_secret": self.settings.google_client_secret,
            "redirect_uri": self.settings.google_redirect_uri,
            "grant_type": "authorization_code",
        }
        return await self._post_form(self.token_url, payload)

    async def refresh_access_token(self, refresh_token: str) -> dict[str, Any]:
        """Refresh an access token from a stored refresh token."""
        self._ensure_oauth_configured()
        payload = {
            "client_id": self.settings.google_client_id,
            "client_secret": self.settings.google_client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        return await self._post_form(self.token_url, payload)

    async def fetch_user_info(self, access_token: str) -> dict[str, Any]:
        """Return Google profile metadata for the authenticated account."""
        return await self._get_json(
            self.user_info_url,
            access_token=access_token,
        )

    async def _post_form(self, url: str, data: dict[str, Any]) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
                response = await client.post(url, data=data)
                response.raise_for_status()
                return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise GoogleIntegrationError(f"Google OAuth request failed: {exc}") from exc

    async def _get_json(self, url: str, access_token: str) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise GoogleIntegrationError(f"Google API request failed: {exc}") from exc

    def _ensure_oauth_configured(self) -> None:
        if not (
            self.settings.google_client_id
            and self.settings.google_client_secret
            and self.settings.google_redirect_uri
        ):
            raise GoogleIntegrationError(
                "Google OAuth is not configured. Set GOOGLE_CLIENT_ID, "
                "GOOGLE_CLIENT_SECRET, and GOOGLE_REDIRECT_URI."
            )


class GoogleBusinessProfileClient:
    """Google Business Profile API client."""

    accounts_url = "https://mybusinessaccountmanagement.googleapis.com/v1/accounts"
    business_information_base_url = "https://mybusinessbusinessinformation.googleapis.com/v1"
    mybusiness_base_url = "https://mybusiness.googleapis.com/v4"

    async def fetch_accounts(self, access_token: str) -> list[dict[str, Any]]:
        """Fetch accessible GBP accounts for the authorized user."""
        payload = await self._get_json(self.accounts_url, access_token)
        accounts = payload.get("accounts", [])
        return accounts if isinstance(accounts, list) else []

    async def fetch_locations(
        self,
        access_token: str,
        account_name: str,
    ) -> list[dict[str, Any]]:
        """Fetch business profiles under a Google business account."""
        read_mask = ",".join(
            [
                "name",
                "title",
                "websiteUri",
                "primaryCategory",
                "storeCode",
                "phoneNumbers",
                "storefrontAddress",
                "latlng",
                "metadata",
                "regularHours",
                "specialHours",
                "profile",
            ]
        )
        url = f"{self.business_information_base_url}/{account_name}/locations"
        params = {"readMask": read_mask, "pageSize": 100}
        payload = await self._get_json(url, access_token, params=params)
        locations = payload.get("locations", [])
        return locations if isinstance(locations, list) else []

    async def fetch_reviews(
        self,
        access_token: str,
        location_name: str,
        page_size: int = 50,
    ) -> list[dict[str, Any]]:
        """Fetch reviews for a location from the MyBusiness v4 API."""
        url = f"{self.mybusiness_base_url}/{location_name}/reviews"
        payload = await self._get_json(url, access_token, params={"pageSize": page_size})
        return payload.get("reviews", [])

    async def reply_to_review(
        self,
        access_token: str,
        location_name: str,
        review_id: str,
        reply_text: str,
    ) -> dict[str, Any]:
        """Post a reply to a review."""
        url = f"{self.mybusiness_base_url}/{location_name}/reviews/{review_id}/reply"
        return await self._put_json(url, access_token, {"comment": reply_text})

    async def delete_review_reply(
        self,
        access_token: str,
        location_name: str,
        review_id: str,
    ) -> None:
        """Delete an existing review reply."""
        url = f"{self.mybusiness_base_url}/{location_name}/reviews/{review_id}/reply"
        await self._delete(url, access_token)

    async def list_posts(
        self,
        access_token: str,
        location_name: str,
    ) -> list[dict[str, Any]]:
        """List active local posts for a location."""
        url = f"{self.mybusiness_base_url}/{location_name}/localPosts"
        payload = await self._get_json(url, access_token)
        return payload.get("localPosts", [])

    async def create_post(
        self,
        access_token: str,
        location_name: str,
        post_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Create a new local post on a GBP location."""
        url = f"{self.mybusiness_base_url}/{location_name}/localPosts"
        return await self._post_json(url, access_token, post_data)

    async def delete_post(
        self,
        access_token: str,
        location_name: str,
        post_id: str,
    ) -> None:
        """Delete a local post."""
        url = f"{self.mybusiness_base_url}/{location_name}/localPosts/{post_id}"
        await self._delete(url, access_token)

    async def _get_json(
        self,
        url: str,
        access_token: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise GoogleIntegrationError(f"Google Business Profile request failed: {exc}") from exc

    async def _post_json(
        self,
        url: str,
        access_token: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise GoogleIntegrationError(f"Google Business Profile request failed: {exc}") from exc

    async def _put_json(
        self,
        url: str,
        access_token: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
                response = await client.put(url, headers=headers, json=data)
                response.raise_for_status()
                return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise GoogleIntegrationError(f"Google Business Profile request failed: {exc}") from exc

    async def _delete(self, url: str, access_token: str) -> None:
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
                response = await client.delete(url, headers=headers)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise GoogleIntegrationError(f"Google Business Profile request failed: {exc}") from exc
