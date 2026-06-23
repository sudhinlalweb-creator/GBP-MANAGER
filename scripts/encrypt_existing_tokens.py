#!/usr/bin/env python3
"""One-time migration: encrypt plaintext refresh tokens already in the database.

Run this BEFORE deploying the new app code that expects encrypted tokens.

Usage:
    cd backend
    FIELD_ENCRYPTION_KEY=<your-key> DATABASE_URL=<your-db-url> python3 ../scripts/encrypt_existing_tokens.py

Safety:
    - Idempotent: rows already holding Fernet ciphertext (starts with 'gAAA') are skipped.
    - Dry-run mode (default): prints what would change without writing.
    - Pass --commit to write to the DB.
"""

from __future__ import annotations

import argparse
import sys
import os

# Ensure the backend app is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import asyncio

from cryptography.fernet import Fernet
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.core.encryption import encrypt_field
from app.google.models import GoogleAccount


FERNET_PREFIX = b"gAAA"  # all Fernet tokens start with this when base64-decoded


def _looks_encrypted(value: str) -> bool:
    """Heuristic: Fernet ciphertexts start with 'gAAA' (base64 of the version byte 0x80)."""
    return value.startswith("gAAA")


async def run(commit: bool) -> None:
    settings = get_settings()
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)  # type: ignore[call-overload]

    async with async_session() as session:
        result = await session.execute(
            select(GoogleAccount).where(GoogleAccount.refresh_token_encrypted.isnot(None))
        )
        accounts = result.scalars().all()

        needs_encryption = [a for a in accounts if not _looks_encrypted(a.refresh_token_encrypted)]
        already_encrypted = len(accounts) - len(needs_encryption)

        print(f"  Total accounts with a refresh token : {len(accounts)}")
        print(f"  Already encrypted (skipping)        : {already_encrypted}")
        print(f"  Plaintext tokens to encrypt         : {len(needs_encryption)}")

        if not needs_encryption:
            print("\n✅ Nothing to do — all tokens are already encrypted.")
            return

        if not commit:
            print("\n[DRY RUN] Would encrypt the following account IDs:")
            for account in needs_encryption:
                print(f"  - {account.id}  ({account.google_email})")
            print("\nRe-run with --commit to apply.")
            return

        for account in needs_encryption:
            account.refresh_token_encrypted = encrypt_field(account.refresh_token_encrypted)

        await session.commit()
        print(f"\n✅ Encrypted {len(needs_encryption)} token(s) and committed.")

    await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Encrypt plaintext refresh tokens in the DB.")
    parser.add_argument("--commit", action="store_true", help="Write changes to DB (default: dry run).")
    args = parser.parse_args()

    asyncio.run(run(commit=args.commit))
