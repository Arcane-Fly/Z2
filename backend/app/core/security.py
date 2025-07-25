"""
Authentication and Security Module for Z2

Provides JWT-based authentication, user management, and security utilities.
"""

from datetime import datetime, timedelta
from typing import Optional, Union

import bcrypt
import structlog
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel

from app.core.config import settings


logger = structlog.get_logger(__name__)

security = HTTPBearer()


class TokenData(BaseModel):
    """Token data structure."""
    username: Optional[str] = None
    user_id: Optional[str] = None
    user_type: Optional[str] = None


class Token(BaseModel):
    """Access token response."""
    access_token: str
    token_type: str
    expires_in: int


class UserCredentials(BaseModel):
    """User login credentials."""
    username: str
    password: str


class PasswordHash:
    """Password hashing utilities."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )


class JWTHandler:
    """JWT token handling utilities."""
    
    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
    
    def create_access_token(
        self,
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a new JWT access token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        logger.debug("Created access token", user_id=data.get("sub"), expires=expire)
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> TokenData:
        """Verify and decode a JWT token."""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            user_id: str = payload.get("user_id")
            user_type: str = payload.get("user_type")
            
            if username is None:
                raise credentials_exception
            
            token_data = TokenData(
                username=username,
                user_id=user_id,
                user_type=user_type
            )
            
            return token_data
            
        except JWTError as e:
            logger.warning("JWT verification failed", error=str(e))
            raise credentials_exception
    
    def create_token_response(
        self,
        user_id: str,
        username: str,
        user_type: str,
    ) -> Token:
        """Create a complete token response."""
        
        # Create token data
        token_data = {
            "sub": username,
            "user_id": user_id,
            "user_type": user_type,
        }
        
        # Generate access token
        access_token = self.create_access_token(data=token_data)
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=self.access_token_expire_minutes * 60,  # Convert to seconds
        )


# Global JWT handler instance
jwt_handler = JWTHandler()


class AuthenticationService:
    """Authentication service for user login and validation."""
    
    def __init__(self):
        self.jwt_handler = jwt_handler
        self.password_hash = PasswordHash()
    
    async def authenticate_user(
        self,
        username: str,
        password: str,
        get_user_func,  # Function to get user from database
    ) -> Optional[dict]:
        """Authenticate a user with username and password."""
        
        # Get user from database
        user = await get_user_func(username)
        
        if not user:
            logger.warning("Authentication failed: user not found", username=username)
            return None
        
        # Verify password
        if not self.password_hash.verify_password(password, user["hashed_password"]):
            logger.warning("Authentication failed: invalid password", username=username)
            return None
        
        # Check if user is active
        if not user.get("is_active", True):
            logger.warning("Authentication failed: user inactive", username=username)
            return None
        
        logger.info("User authenticated successfully", username=username, user_id=user["id"])
        
        return user
    
    def create_user_token(self, user: dict) -> Token:
        """Create an access token for an authenticated user."""
        
        return self.jwt_handler.create_token_response(
            user_id=str(user["id"]),
            username=user["username"],
            user_type=user.get("user_type", "operator"),
        )
    
    async def verify_token(self, token: str) -> TokenData:
        """Verify an access token."""
        return self.jwt_handler.verify_token(token)


# Global authentication service instance
auth_service = AuthenticationService()


class SecurityMiddleware:
    """Security middleware for API protection."""
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """Validate API key for external integrations."""
        # TODO: Implement API key validation
        # This would check against stored API keys in the database
        return True
    
    @staticmethod
    def check_rate_limit(user_id: str, endpoint: str) -> bool:
        """Check rate limiting for user and endpoint."""
        # TODO: Implement rate limiting logic
        # This would use Redis to track request counts
        return True
    
    @staticmethod
    def validate_permissions(user: dict, required_permission: str) -> bool:
        """Validate user permissions for specific actions."""
        
        # Superusers have all permissions
        if user.get("is_superuser", False):
            return True
        
        # Basic permission checks
        user_type = user.get("user_type", "operator")
        
        # Define permission mappings
        permissions = {
            "developer": [
                "read_agents",
                "write_agents",
                "read_workflows",
                "write_workflows",
                "read_models",
                "configure_models",
                "read_users",
                "system_admin",
            ],
            "operator": [
                "read_agents",
                "read_workflows",
                "execute_workflows",
                "read_models",
            ],
        }
        
        user_permissions = permissions.get(user_type, [])
        
        return required_permission in user_permissions


# Global security middleware instance
security_middleware = SecurityMiddleware()


def get_password_hash(password: str) -> str:
    """Convenience function to hash passwords."""
    return PasswordHash.hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Convenience function to verify passwords."""
    return PasswordHash.verify_password(plain_password, hashed_password)