"""Services for Google OAuth, profile synchronization, and dashboard aggregation."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import jwt
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import OrganizationContext
from app.core.config import get_settings
from app.google.client import GoogleBusinessProfileClient, GoogleIntegrationError, GoogleOAuthClient
from app.google.models import GoogleAccount, GoogleBusinessProfile
from app.schemas.google import (
    GoogleAccountResponse,
    GoogleBusinessProfileResponse,
    GoogleDashboardResponse,
    GoogleIntegrationStatusResponse,
    GoogleOAuthConnectResponse,
    GoogleSyncResult,
)


class GoogleIntegrationService:
    """Tenant-scoped orchestration for Google integration workflows."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.oauth_client = GoogleOAuthClient()
        self.gbp_client = GoogleBusinessProfileClient()

    def build_connect_response(
        self,
        context: OrganizationContext,
    ) -> GoogleOAuthConnectResponse:
        """Build a Google OAuth connect URL scoped to the current organization."""
        state = self._encode_state(
            organization_id=context.organization.id,
            user_id=context.user.id,
        )
        return GoogleOAuthConnectResponse(
            authorization_url=self.oauth_client.build_authorization_url(state),
            state=state,
        )

    async def exchange_callback(
        self,
        db_session: AsyncSession,
        context: OrganizationContext,
        code: str,
        state: str,
    ) -> GoogleAccountResponse:
        """Exchange the callback code, upsert the account, and return the safe payload."""
        payload = self._decode_state(state)
        if payload["organization_id"] != str(context.organization.id) or payload["user_id"] != str(
            context.user.id
        ):
            raise GoogleIntegrationError("Google OAuth state does not match the active organization.")

        tokens = await self.oauth_client.exchange_code_for_tokens(code)
        access_token = tokens.get("access_token")
        if not isinstance(access_token, str) or not access_token:
            raise GoogleIntegrationError("Google OAuth callback did not return an access token.")

        user_info = await self.oauth_client.fetch_user_info(access_token)
        email = user_info.get("email")
        if not isinstance(email, str) or not email.strip():
            raise GoogleIntegrationError("Google OAuth callback did not return an email address.")

        refresh_token = tokens.get("refresh_token")
        expires_in = tokens.get("expires_in")
        expires_at = None
        if isinstance(expires_in, int):
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

        statement = select(GoogleAccount).where(
            GoogleAccount.organization_id == context.organization.id,
            GoogleAccount.google_email == email.strip().lower(),
        )
        google_account = await db_session.scalar(statement)

        if google_account is None:
            google_account = GoogleAccount(
                organization_id=context.organization.id,
                google_email=email.strip().lower(),
            )
            db_session.add(google_account)

        if isinstance(refresh_token, str) and refresh_token:
            # Transitional storage until encrypted secret management is introduced.
            google_account.refresh_token_encrypted = refresh_token
        google_account.access_token_expires_at = expires_at.isoformat() if expires_at else None

        await db_session.commit()
        await db_session.refresh(google_account)
        return GoogleAccountResponse.model_validate(google_account)

    async def get_integration_status(
        self,
        db_session: AsyncSession,
        context: OrganizationContext,
    ) -> GoogleIntegrationStatusResponse:
        """Return per-organization readiness and summary counts."""
        connected_accounts = await db_session.scalar(
            select(func.count(GoogleAccount.id)).where(
                GoogleAccount.organization_id == context.organization.id,
            )
        )
        synced_profiles = await db_session.scalar(
            select(func.count(GoogleBusinessProfile.id)).where(
                GoogleBusinessProfile.organization_id == context.organization.id,
            )
        )
        last_profile_sync_at = await db_session.scalar(
            select(func.max(GoogleBusinessProfile.updated_at)).where(
                GoogleBusinessProfile.organization_id == context.organization.id,
            )
        )

        return GoogleIntegrationStatusResponse(
            organization_id=context.organization.id,
            organization_name=context.organization.name,
            organization_role=context.membership.role,
            google_oauth_configured=bool(
                self.settings.google_client_id
                and self.settings.google_client_secret
                and self.settings.google_redirect_uri
            ),
            google_maps_configured=bool(self.settings.google_maps_api_key),
            worker_configured=bool(self.settings.redis_host and self.settings.celery_default_queue),
            connected_accounts=int(connected_accounts or 0),
            synced_profiles=int(synced_profiles or 0),
            last_profile_sync_at=last_profile_sync_at,
        )

    async def get_dashboard(
        self,
        db_session: AsyncSession,
        context: OrganizationContext,
    ) -> GoogleDashboardResponse:
        """Return a summary dashboard of connected Google accounts and synced profiles."""
        accounts = (
            (
                await db_session.execute(
                    select(GoogleAccount)
                    .where(GoogleAccount.organization_id == context.organization.id)
                    .order_by(GoogleAccount.created_at.desc())
                )
            )
            .scalars()
            .all()
        )
        profiles = (
            (
                await db_session.execute(
                    select(GoogleBusinessProfile)
                    .where(GoogleBusinessProfile.organization_id == context.organization.id)
                    .order_by(GoogleBusinessProfile.updated_at.desc())
                    .limit(20)
                )
            )
            .scalars()
            .all()
        )
        linked_locations = sum(1 for profile in profiles if profile.location_id is not None)
        last_profile_sync_at = max((profile.updated_at for profile in profiles), default=None)

        return GoogleDashboardResponse(
            organization_id=context.organization.id,
            organization_name=context.organization.name,
            connected_accounts=len(accounts),
            synced_profiles=await self._count_profiles(db_session, context.organization.id),
            linked_locations=linked_locations,
            last_profile_sync_at=last_profile_sync_at,
            accounts=[GoogleAccountResponse.model_validate(account) for account in accounts],
            profiles=[GoogleBusinessProfileResponse.model_validate(profile) for profile in profiles],
        )

    async def sync_google_account(
        self,
        db_session: AsyncSession,
        organization_id: UUID,
        google_account_id: UUID,
    ) -> GoogleSyncResult:
        """Fetch Google Business Profile data and upsert it into the local database."""
        google_account = await db_session.get(GoogleAccount, google_account_id)
        if google_account is None or google_account.organization_id != organization_id:
            raise GoogleIntegrationError("Google account was not found for the organization.")
        if not google_account.refresh_token_encrypted:
            raise GoogleIntegrationError(
                "Google account does not have a refresh token. Reconnect with consent."
            )

        token_payload = await self.oauth_client.refresh_access_token(
            google_account.refresh_token_encrypted
        )
        access_token = token_payload.get("access_token")
        if not isinstance(access_token, str) or not access_token:
            raise GoogleIntegrationError("Google access token refresh did not return an access token.")

        accounts = await self.gbp_client.fetch_accounts(access_token)
        profiles_synced = 0
        for account in accounts:
            account_name = account.get("name")
            if not isinstance(account_name, str) or not account_name:
                continue

            locations = await self.gbp_client.fetch_locations(access_token, account_name)
            profiles_synced += await self._upsert_locations(
                db_session=db_session,
                organization_id=organization_id,
                google_account_id=google_account_id,
                locations=locations,
            )

        await db_session.commit()

        return GoogleSyncResult(
            organization_id=organization_id,
            google_account_id=google_account_id,
            connected_email=google_account.google_email,
            accounts_fetched=len(accounts),
            profiles_synced=profiles_synced,
            raw_accounts=accounts,
        )

    def _encode_state(self, organization_id: UUID, user_id: UUID) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "organization_id": str(organization_id),
            "user_id": str(user_id),
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=10)).timestamp()),
            "purpose": "google-oauth",
        }
        return jwt.encode(
            payload,
            self.settings.secret_key,
            algorithm=self.settings.jwt_algorithm,
        )

    def _decode_state(self, state: str) -> dict[str, str]:
        try:
            payload = jwt.decode(
                state,
                self.settings.secret_key,
                algorithms=[self.settings.jwt_algorithm],
            )
        except jwt.PyJWTError as exc:
            raise GoogleIntegrationError("Google OAuth state is invalid or expired.") from exc

        if payload.get("purpose") != "google-oauth":
            raise GoogleIntegrationError("Google OAuth state purpose is invalid.")
        return {
            "organization_id": str(payload["organization_id"]),
            "user_id": str(payload["user_id"]),
        }

    async def _count_profiles(self, db_session: AsyncSession, organization_id: UUID) -> int:
        count = await db_session.scalar(
            select(func.count(GoogleBusinessProfile.id)).where(
                GoogleBusinessProfile.organization_id == organization_id,
            )
        )
        return int(count or 0)

    async def _upsert_locations(
        self,
        db_session: AsyncSession,
        organization_id: UUID,
        google_account_id: UUID,
        locations: list[dict[str, Any]],
    ) -> int:
        upserted = 0
        for location in locations:
            title = location.get("title")
            if not isinstance(title, str) or not title.strip():
                continue

            statement = select(GoogleBusinessProfile).where(
                GoogleBusinessProfile.organization_id == organization_id,
                GoogleBusinessProfile.google_account_id == google_account_id,
                GoogleBusinessProfile.google_location_name == title.strip(),
            )
            profile = await db_session.scalar(statement)
            primary_category = location.get("primaryCategory", {})
            category_name = None
            if isinstance(primary_category, dict):
                category_name = primary_category.get("displayName")
            website_url = location.get("websiteUri")

            if profile is None:
                profile = GoogleBusinessProfile(
                    organization_id=organization_id,
                    google_account_id=google_account_id,
                    google_location_name=title.strip(),
                )
                db_session.add(profile)

            profile.primary_category = category_name if isinstance(category_name, str) else None
            profile.website_url = website_url if isinstance(website_url, str) else None
            upserted += 1

        return upserted
