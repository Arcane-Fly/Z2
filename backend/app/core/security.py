"""
Authentication and Security Module for Z2

Provides JWT-based authentication, user management, and security utilities
with enhanced security features for production deployment.
"""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import structlog
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings

logger = structlog.get_logger(__name__)

# Enhanced password context with multiple schemes
pwd_context = CryptContext(
    schemes=["bcrypt", "pbkdf2_sha256"],
    default="bcrypt",
    deprecated="auto",
    bcrypt__rounds=12,  # Increased rounds for better security
)

security = HTTPBearer(auto_error=False)


class TokenData(BaseModel):
    """Token data structure with enhanced security metadata."""

    username: str | None = None
    user_id: str | None = None
    user_type: str | None = None
    permissions: list[str] = Field(default_factory=list)
    issued_at: datetime | None = None
    session_id: str | None = None


class Token(BaseModel):
    """Access token response with refresh token support."""

    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int
    scope: str | None = None


class UserCredentials(BaseModel):
    """User login credentials with validation."""

    username: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    remember_me: bool = False


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""

    refresh_token: str


class SecurityConfig:
    """Security configuration and constants."""

    ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
    REFRESH_TOKEN_EXPIRE_DAYS = 30
    ALGORITHM = settings.algorithm
    SECRET_KEY = settings.secret_key

    # Rate limiting
    MAX_LOGIN_ATTEMPTS = 5
    LOGIN_COOLDOWN_MINUTES = 15

    # Session management
    MAX_CONCURRENT_SESSIONS = 3

    # CORS
    ALLOWED_ORIGINS = settings.cors_origins_list
    ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    ALLOWED_HEADERS = ["*"]
    ALLOW_CREDENTIALS = True


class PasswordSecurity:
    """Enhanced password security utilities."""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error("Password verification failed", error=str(e))
            return False

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password with salt."""
        return pwd_context.hash(password)

    @staticmethod
    def validate_password_strength(password: str) -> dict[str, Any]:
        """Validate password strength according to security policies."""
        errors = []
        score = 0

        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        elif len(password) >= 12:
            score += 2
        else:
            score += 1

        if not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        else:
            score += 1

        if not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        else:
            score += 1

        if not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one digit")
        else:
            score += 1

        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            errors.append("Password must contain at least one special character")
        else:
            score += 1

        strength_levels = {
            0: "Very Weak",
            1: "Weak",
            2: "Fair",
            3: "Good",
            4: "Strong",
            5: "Very Strong",
            6: "Excellent"
        }

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "score": score,
            "strength": strength_levels.get(score, "Unknown")
        }


class JWTManager:
    """Enhanced JWT token management with refresh tokens and security features."""

    def __init__(self):
        self.secret_key = SecurityConfig.SECRET_KEY
        self.algorithm = SecurityConfig.ALGORITHM
        self.access_token_expire_minutes = SecurityConfig.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = SecurityConfig.REFRESH_TOKEN_EXPIRE_DAYS

    def create_access_token(
        self,
        data: dict[str, Any],
        expires_delta: timedelta | None = None
    ) -> str:
        """Create a new JWT access token with enhanced security."""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(
                minutes=self.access_token_expire_minutes
            )

        # Add security metadata
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(UTC),
            "jti": secrets.token_urlsafe(32),  # JWT ID for tracking
            "typ": "access_token"
        })

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

        logger.info("Access token created",
                   user_id=data.get("user_id"),
                   expires=expire.isoformat())

        return encoded_jwt

    def create_refresh_token(self, user_id: str, session_id: str) -> str:
        """Create a refresh token."""
        data = {
            "user_id": user_id,
            "session_id": session_id,
            "typ": "refresh_token",
            "exp": datetime.now(UTC) + timedelta(days=self.refresh_token_expire_days),
            "iat": datetime.now(UTC),
            "jti": secrets.token_urlsafe(32)
        }

        return jwt.encode(data, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str, token_type: str = "access_token") -> TokenData:
        """Verify and decode a JWT token with enhanced validation."""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Verify token type
            if payload.get("typ") != token_type:
                raise credentials_exception

            # Extract claims
            username = payload.get("sub")
            user_id = payload.get("user_id")
            user_type = payload.get("user_type", "user")
            permissions = payload.get("permissions", [])
            session_id = payload.get("session_id")
            issued_at = payload.get("iat")

            if username is None or user_id is None:
                raise credentials_exception

            token_data = TokenData(
                username=username,
                user_id=user_id,
                user_type=user_type,
                permissions=permissions,
                session_id=session_id,
                issued_at=datetime.fromtimestamp(issued_at, tz=UTC) if issued_at else None
            )

            return token_data

        except JWTError as e:
            logger.warning("JWT verification failed", error=str(e), token_type=token_type)
            raise credentials_exception

    def create_token_pair(
        self,
        user_id: str,
        username: str,
        user_type: str = "user",
        permissions: list[str] = None,
        remember_me: bool = False
    ) -> Token:
        """Create access and refresh token pair."""
        if permissions is None:
            permissions = []

        session_id = secrets.token_urlsafe(32)

        # Create access token data
        access_data = {
            "sub": username,
            "user_id": user_id,
            "user_type": user_type,
            "permissions": permissions,
            "session_id": session_id
        }

        # Generate tokens
        access_token = self.create_access_token(data=access_data)

        # Create refresh token if remember_me or long session
        refresh_token = None
        if remember_me:
            refresh_token = self.create_refresh_token(user_id, session_id)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=self.access_token_expire_minutes * 60,
            scope=" ".join(permissions) if permissions else None
        )

    async def store_refresh_token(
        self,
        db: AsyncSession,
        refresh_token: str,
        user_id: str,
        session_id: str,
        expires_at: datetime
    ) -> None:
        """Store refresh token in database."""
        from app.models.role import RefreshToken

        # Hash the token for storage
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

        refresh_token_record = RefreshToken(
            token_hash=token_hash,
            user_id=user_id,
            session_id=session_id,
            expires_at=expires_at
        )

        db.add(refresh_token_record)
        await db.commit()

    async def verify_refresh_token(
        self,
        db: AsyncSession,
        refresh_token: str
    ) -> TokenData | None:
        """Verify refresh token and check if it's in database."""
        from app.models.role import RefreshToken

        try:
            # First verify JWT
            token_data = self.verify_token(refresh_token, token_type="refresh_token")

            # Then check if token exists in database and is not revoked
            token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

            stmt = select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.is_revoked is False,
                RefreshToken.expires_at > datetime.now(UTC)
            )
            result = await db.execute(stmt)
            db_token = result.scalar_one_or_none()

            if not db_token:
                return None

            # Update last used timestamp
            stmt = update(RefreshToken).where(
                RefreshToken.id == db_token.id
            ).values(last_used=datetime.now(UTC))
            await db.execute(stmt)
            await db.commit()

            return token_data

        except Exception as e:
            logger.warning("Refresh token verification failed", error=str(e))
            return None

    async def revoke_refresh_token(
        self,
        db: AsyncSession,
        refresh_token: str
    ) -> bool:
        """Revoke a refresh token."""
        from app.models.role import RefreshToken

        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

        stmt = update(RefreshToken).where(
            RefreshToken.token_hash == token_hash
        ).values(is_revoked=True)

        result = await db.execute(stmt)
        await db.commit()

        return result.rowcount > 0

    async def revoke_user_tokens(
        self,
        db: AsyncSession,
        user_id: str
    ) -> int:
        """Revoke all refresh tokens for a user."""
        from app.models.role import RefreshToken

        stmt = update(RefreshToken).where(
            RefreshToken.user_id == user_id
        ).values(is_revoked=True)

        result = await db.execute(stmt)
        await db.commit()

        return result.rowcount

    async def cleanup_expired_tokens(self, db: AsyncSession) -> int:
        """Clean up expired refresh tokens."""
        from app.models.role import RefreshToken

        # Delete expired tokens
        stmt = RefreshToken.__table__.delete().where(
            RefreshToken.expires_at < datetime.now(UTC)
        )

        result = await db.execute(stmt)
        await db.commit()

        return result.rowcount


class SecurityHeaders:
    """Security headers middleware configuration."""

    @staticmethod
    def get_security_headers() -> dict[str, str]:
        """Get recommended security headers for production."""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }


class RateLimiter:
    """Simple in-memory rate limiter for authentication attempts."""

    def __init__(self):
        self._attempts: dict[str, list[datetime]] = {}
        self._blocked: dict[str, datetime] = {}

    def is_blocked(self, identifier: str) -> bool:
        """Check if identifier is currently blocked."""
        if identifier in self._blocked:
            if datetime.now(UTC) > self._blocked[identifier]:
                del self._blocked[identifier]
                return False
            return True
        return False

    def record_attempt(self, identifier: str, success: bool = False) -> bool:
        """Record an authentication attempt."""
        now = datetime.now(UTC)

        # Clean old attempts
        if identifier in self._attempts:
            self._attempts[identifier] = [
                attempt for attempt in self._attempts[identifier]
                if now - attempt < timedelta(minutes=SecurityConfig.LOGIN_COOLDOWN_MINUTES)
            ]

        if success:
            # Clear attempts on success
            if identifier in self._attempts:
                del self._attempts[identifier]
            return True

        # Record failed attempt
        if identifier not in self._attempts:
            self._attempts[identifier] = []

        self._attempts[identifier].append(now)

        # Check if should block
        if len(self._attempts[identifier]) >= SecurityConfig.MAX_LOGIN_ATTEMPTS:
            self._blocked[identifier] = now + timedelta(minutes=SecurityConfig.LOGIN_COOLDOWN_MINUTES)
            return False

        return True


# Global instances
jwt_manager = JWTManager()
rate_limiter = RateLimiter()


class AuthenticationService:
    """Enhanced authentication service with security features."""

    def __init__(self):
        self.jwt_manager = jwt_manager
        self.password_security = PasswordSecurity()
        self.rate_limiter = rate_limiter

    async def authenticate_user(
        self,
        credentials: UserCredentials,
        get_user_func,
        request: Request | None = None
    ) -> Token | None:
        """Authenticate user with enhanced security checks."""

        # Rate limiting by IP or username
        identifier = credentials.username
        if request and hasattr(request, 'client'):
            identifier = f"{request.client.host}:{credentials.username}"

        # Check if blocked
        if self.rate_limiter.is_blocked(identifier):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts. Please try again later."
            )

        try:
            # Get user from database
            user = await get_user_func(credentials.username)
            if not user:
                self.rate_limiter.record_attempt(identifier, success=False)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password"
                )

            # Verify password
            if not self.password_security.verify_password(
                credentials.password,
                user.get("password_hash", "")
            ):
                self.rate_limiter.record_attempt(identifier, success=False)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password"
                )

            # Check if user is active
            if not user.get("is_active", True):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Account is disabled"
                )

            # Success - record and create tokens
            self.rate_limiter.record_attempt(identifier, success=True)

            return self.jwt_manager.create_token_pair(
                user_id=user["id"],
                username=user["username"],
                user_type=user.get("user_type", "user"),
                permissions=user.get("permissions", []),
                remember_me=credentials.remember_me
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error("Authentication error", error=str(e))
            self.rate_limiter.record_attempt(identifier, success=False)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service error"
            )

    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials,
        get_user_func
    ) -> dict[str, Any]:
        """Get current user from JWT token."""
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )

        token_data = self.jwt_manager.verify_token(credentials.credentials)
        user = await get_user_func(token_data.username)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        return user

    async def refresh_access_token(
        self,
        refresh_request: RefreshTokenRequest,
        get_user_func
    ) -> Token:
        """Refresh access token using refresh token."""
        try:
            token_data = self.jwt_manager.verify_token(
                refresh_request.refresh_token,
                token_type="refresh_token"
            )

            user = await get_user_func(token_data.user_id)
            if not user or not user.get("is_active", True):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )

            return self.jwt_manager.create_token_pair(
                user_id=user["id"],
                username=user["username"],
                user_type=user.get("user_type", "user"),
                permissions=user.get("permissions", [])
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error("Token refresh error", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )


# Global authentication service
auth_service = AuthenticationService()
