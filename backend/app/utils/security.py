"""
Security utilities for the Z2 platform.
"""

import hashlib
import secrets
from datetime import UTC, datetime
from typing import Optional


def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token.

    Args:
        length: Token length in bytes

    Returns:
        Hexadecimal token string
    """
    return secrets.token_hex(length)


def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """Hash a password with salt.

    Args:
        password: Plain text password
        salt: Optional salt (generated if not provided)

    Returns:
        Tuple of (hashed_password, salt)
    """
    if salt is None:
        salt = secrets.token_hex(32)

    # Create hash
    pwd_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
    )

    return pwd_hash.hex(), salt


def verify_password(password: str, hashed_password: str, salt: str) -> bool:
    """Verify a password against its hash.

    Args:
        password: Plain text password
        hashed_password: Stored password hash
        salt: Password salt

    Returns:
        True if password matches
    """
    pwd_hash, _ = hash_password(password, salt)
    return pwd_hash == hashed_password


def get_utc_now() -> datetime:
    """Get current UTC timestamp.

    Returns:
        Current UTC datetime
    """
    return datetime.now(UTC)


def is_expired(expires_at: datetime) -> bool:
    """Check if a timestamp has expired.

    Args:
        expires_at: Expiration timestamp

    Returns:
        True if expired
    """
    return get_utc_now() > expires_at


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename for safe storage.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    import re

    # Remove potentially dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', "_", filename)
    # Remove control characters
    filename = "".join(c for c in filename if ord(c) >= 32)
    # Limit length
    return filename[:255]
