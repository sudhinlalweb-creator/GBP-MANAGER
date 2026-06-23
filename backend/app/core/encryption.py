"""Symmetric field-level encryption for sensitive database columns.

Usage:
    from app.core.encryption import encrypt_field, decrypt_field

    stored = encrypt_field(raw_token)          # before DB write
    raw    = decrypt_field(stored_ciphertext)  # after DB read

Key management:
    Set FIELD_ENCRYPTION_KEY in env to a Fernet key (base64-urlsafe, 32 bytes).
    Generate a new key:
        python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

    To rotate the key: run scripts/rotate_field_encryption.py with OLD_KEY and NEW_KEY set.
"""

from __future__ import annotations

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import get_settings


def _fernet() -> Fernet:
    """Return a Fernet instance keyed from settings. Fails fast if key is missing or invalid."""
    key = get_settings().field_encryption_key
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt_field(plaintext: str) -> str:
    """Encrypt a plaintext string and return a URL-safe base64 ciphertext string."""
    return _fernet().encrypt(plaintext.encode()).decode()


def decrypt_field(ciphertext: str) -> str:
    """Decrypt a ciphertext string produced by encrypt_field.

    Raises ValueError on tampered or key-mismatched input — callers should treat
    this as a re-auth event (token revoked/rotated) rather than a hard crash.
    """
    try:
        return _fernet().decrypt(ciphertext.encode()).decode()
    except InvalidToken as exc:
        raise ValueError("Field decryption failed — token may be corrupt or the key has rotated.") from exc
