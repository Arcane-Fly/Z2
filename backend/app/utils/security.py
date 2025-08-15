"""
Security utilities for the Z2 platform.
"""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Optional
import bcrypt
import jwt


# JWT Configuration
SECRET_KEY = "your-secret-key-change-in-production"  # Should be from environment
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token.

    Args:
        length: Token length in bytes

    Returns:
        Hexadecimal token string
    """
    return secrets.token_hex(length)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash.

    Args:
        password: Plain text password
        hashed_password: Stored password hash

    Returns:
        True if password matches
    """
    pwd_bytes = password.encode('utf-8')
    hash_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(pwd_bytes, hash_bytes)


def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token.
    
    Args:
        user_id: User identifier
        expires_delta: Optional custom expiration time
        
    Returns:
        JWT token string
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode = {"sub": user_id, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str) -> str:
    """Verify and decode a JWT access token.
    
    Args:
        token: JWT token string
        
    Returns:
        User ID from token
        
    Raises:
        Exception: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise Exception("Invalid token: no user ID")
        return user_id
    except jwt.PyJWTError as e:
        raise Exception(f"Invalid token: {e}")


def hash_password_legacy(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """Legacy hash a password with salt (for backward compatibility).

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


def verify_password_legacy(password: str, hashed_password: str, salt: str) -> bool:
    """Legacy verify a password against its hash.

    Args:
        password: Plain text password
        hashed_password: Stored password hash
        salt: Password salt

    Returns:
        True if password matches
    """
    pwd_hash, _ = hash_password_legacy(password, salt)
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
