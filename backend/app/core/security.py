"""Authentication helpers for password hashing and JWT handling."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from fastapi import HTTPException, status
from jwt import ExpiredSignatureError, InvalidTokenError
from passlib.context import CryptContext

from app.core.config import get_settings


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()
REFRESH_TOKEN_EXPIRE_DAYS = 7


def _build_token(
    *,
    subject: str,
    token_type: str,
    expires_delta: timedelta,
) -> str:
    """Return a signed JWT for the supplied subject and token type."""
    now = datetime.now(timezone.utc)
    expire_at = now + expires_delta
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int(expire_at.timestamp()),
    }
    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )


def hash_password(plain: str) -> str:
    """Return a secure password hash."""
    return password_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Return True when a password matches the stored hash."""
    return password_context.verify(plain, hashed)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """Return a signed JWT access token."""
    return _build_token(
        subject=subject,
        token_type="access",
        expires_delta=expires_delta
        or timedelta(minutes=settings.access_token_expire_minutes),
    )


def create_refresh_token(subject: str) -> str:
    """Return a signed JWT refresh token with a seven-day expiry."""
    return _build_token(
        subject=subject,
        token_type="refresh",
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT token or raise a 401 HTTP exception."""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token subject is missing.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


def decode_access_token(token: str) -> dict[str, Any]:
    """Backward-compatible alias for access token decoding."""
    return decode_token(token)
