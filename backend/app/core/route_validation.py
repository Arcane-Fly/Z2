"""
Route Validation and Boundary Management for Z2 API

This module provides comprehensive route validation, boundary enforcement,
and API security controls to ensure proper separation of concerns and access control.
"""

import re
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Set

import structlog
from fastapi import HTTPException, Request, status
from fastapi.routing import APIRouter

from app.core.config import settings

logger = structlog.get_logger(__name__)


class RouteScope:
    """Defines route scopes for boundary enforcement."""
    
    PUBLIC = "public"           # No authentication required
    AUTHENTICATED = "authenticated"  # Basic authentication required
    ADMIN = "admin"            # Admin privileges required
    SERVICE = "service"        # Service-to-service communication
    DEBUG = "debug"            # Debug/development only


class RouteBoundary:
    """Route boundary definition with validation rules."""
    
    def __init__(
        self,
        scope: str,
        allowed_methods: Set[str] = None,
        rate_limit: Optional[int] = None,
        required_permissions: List[str] = None,
        allowed_origins: List[str] = None,
        content_type_restrictions: List[str] = None
    ):
        self.scope = scope
        self.allowed_methods = allowed_methods or {"GET", "POST", "PUT", "DELETE", "PATCH"}
        self.rate_limit = rate_limit
        self.required_permissions = required_permissions or []
        self.allowed_origins = allowed_origins or []
        self.content_type_restrictions = content_type_restrictions or []


class RouteRegistry:
    """Central registry for route boundaries and validation rules."""
    
    def __init__(self):
        self.boundaries: Dict[str, RouteBoundary] = {}
        self.route_patterns: Dict[str, str] = {}
        self._setup_default_boundaries()
    
    def _setup_default_boundaries(self):
        """Setup default route boundaries for Z2 API."""
        
        # Public routes (no authentication)
        self.register_boundary("auth", RouteBoundary(
            scope=RouteScope.PUBLIC,
            allowed_methods={"POST"},
            rate_limit=10,  # 10 requests per minute
            content_type_restrictions=["application/json"]
        ))
        
        # Authenticated user routes
        self.register_boundary("users", RouteBoundary(
            scope=RouteScope.AUTHENTICATED,
            allowed_methods={"GET", "PUT", "PATCH"},
            rate_limit=100,
            required_permissions=["user:read", "user:write"]
        ))
        
        # Admin routes
        self.register_boundary("api-keys", RouteBoundary(
            scope=RouteScope.ADMIN,
            allowed_methods={"GET", "POST", "DELETE"},
            rate_limit=50,
            required_permissions=["admin:api_keys"]
        ))
        
        # Agent execution routes
        self.register_boundary("agents", RouteBoundary(
            scope=RouteScope.AUTHENTICATED,
            allowed_methods={"GET", "POST", "PUT", "DELETE"},
            rate_limit=50,
            required_permissions=["agent:execute", "agent:manage"]
        ))
        
        # Workflow management routes
        self.register_boundary("workflows", RouteBoundary(
            scope=RouteScope.AUTHENTICATED,
            allowed_methods={"GET", "POST", "PUT", "DELETE"},
            rate_limit=30,
            required_permissions=["workflow:read", "workflow:write"]
        ))
        
        # Model management routes
        self.register_boundary("models", RouteBoundary(
            scope=RouteScope.AUTHENTICATED,
            allowed_methods={"GET", "POST", "PUT"},
            rate_limit=20,
            required_permissions=["model:read", "model:configure"]
        ))
        
        # MCP routes (high privilege)
        self.register_boundary("mcp", RouteBoundary(
            scope=RouteScope.AUTHENTICATED,
            allowed_methods={"GET", "POST", "PUT"},
            rate_limit=100,
            required_permissions=["mcp:execute", "mcp:monitor"]
        ))
        
        # Consent management
        self.register_boundary("consent", RouteBoundary(
            scope=RouteScope.AUTHENTICATED,
            allowed_methods={"GET", "POST", "PUT", "DELETE"},
            rate_limit=30,
            required_permissions=["consent:read", "consent:write"]
        ))
        
        # A2A (Agent-to-Agent) communication
        self.register_boundary("a2a", RouteBoundary(
            scope=RouteScope.SERVICE,
            allowed_methods={"POST", "PUT"},
            rate_limit=200,
            required_permissions=["a2a:communicate"]
        ))
        
        # Activity monitoring
        self.register_boundary("activity", RouteBoundary(
            scope=RouteScope.AUTHENTICATED,
            allowed_methods={"GET"},
            rate_limit=100,
            required_permissions=["activity:read"]
        ))
        
        # Quantum computing routes
        self.register_boundary("multi-agent-system/quantum", RouteBoundary(
            scope=RouteScope.AUTHENTICATED,
            allowed_methods={"GET", "POST", "PUT"},
            rate_limit=10,  # Computationally expensive
            required_permissions=["quantum:execute", "quantum:read"]
        ))
        
        # Debug routes (development only)
        self.register_boundary("debug", RouteBoundary(
            scope=RouteScope.DEBUG,
            allowed_methods={"GET", "POST"},
            rate_limit=20,
            required_permissions=["debug:access"]
        ))
    
    def register_boundary(self, route_prefix: str, boundary: RouteBoundary):
        """Register a route boundary for a specific route prefix."""
        self.boundaries[route_prefix] = boundary
        logger.info("Route boundary registered", prefix=route_prefix, scope=boundary.scope)
    
    def get_boundary(self, route_path: str) -> Optional[RouteBoundary]:
        """Get the boundary configuration for a route path."""
        # Extract the route prefix from the path
        prefix = self._extract_route_prefix(route_path)
        return self.boundaries.get(prefix)
    
    def _extract_route_prefix(self, route_path: str) -> str:
        """Extract the route prefix from a full route path."""
        # Remove /api/v1/ prefix and get first segment
        path = route_path.replace("/api/v1/", "").strip("/")
        segments = path.split("/")
        
        # Handle nested routes like multi-agent-system/quantum
        if len(segments) >= 2 and segments[0] == "multi-agent-system":
            return "/".join(segments[:2])
        
        return segments[0] if segments else ""


class RouteValidator:
    """Validates routes against defined boundaries and security policies."""
    
    def __init__(self, registry: RouteRegistry):
        self.registry = registry
    
    def validate_route_access(
        self,
        request: Request,
        route_path: str,
        user_permissions: List[str] = None
    ) -> bool:
        """Validate if a request is allowed to access a specific route."""
        boundary = self.registry.get_boundary(route_path)
        if not boundary:
            logger.warning("No boundary defined for route", path=route_path)
            return False
        
        # Check method allowed
        if request.method not in boundary.allowed_methods:
            logger.warning(
                "Method not allowed",
                method=request.method,
                path=route_path,
                allowed=list(boundary.allowed_methods)
            )
            return False
        
        # Check scope-based access
        if boundary.scope == RouteScope.DEBUG and not settings.debug:
            logger.warning("Debug route accessed in production", path=route_path)
            return False
        
        # Check permissions if required
        user_permissions = user_permissions or []
        if boundary.required_permissions:
            if not any(perm in user_permissions for perm in boundary.required_permissions):
                logger.warning(
                    "Insufficient permissions",
                    required=boundary.required_permissions,
                    user_permissions=user_permissions
                )
                return False
        
        return True
    
    def validate_content_type(self, request: Request, route_path: str) -> bool:
        """Validate request content type against route restrictions."""
        boundary = self.registry.get_boundary(route_path)
        if not boundary or not boundary.content_type_restrictions:
            return True
        
        content_type = request.headers.get("content-type", "").split(";")[0]
        return content_type in boundary.content_type_restrictions


# Global route registry instance
route_registry = RouteRegistry()
route_validator = RouteValidator(route_registry)


def enforce_route_boundary(f: Callable) -> Callable:
    """Decorator to enforce route boundary validation on FastAPI endpoints."""
    
    @wraps(f)
    async def wrapper(*args, **kwargs):
        # Extract request from kwargs or args
        request = None
        for arg in list(args) + list(kwargs.values()):
            if isinstance(arg, Request):
                request = arg
                break
        
        if not request:
            logger.error("No request object found for route boundary enforcement")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
        
        route_path = request.url.path
        
        # Get user permissions (this would typically come from JWT token or session)
        user_permissions = getattr(request.state, "user_permissions", [])
        
        # Validate route access
        if not route_validator.validate_route_access(request, route_path, user_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this route"
            )
        
        # Validate content type for POST/PUT requests
        if request.method in {"POST", "PUT", "PATCH"}:
            if not route_validator.validate_content_type(request, route_path):
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail="Unsupported content type for this route"
                )
        
        return await f(*args, **kwargs)
    
    return wrapper


def create_bounded_router(
    prefix: str,
    boundary: Optional[RouteBoundary] = None,
    **router_kwargs
) -> APIRouter:
    """Create a FastAPI router with automatic boundary enforcement."""
    
    router = APIRouter(prefix=f"/{prefix}", **router_kwargs)
    
    # Register custom boundary if provided
    if boundary:
        route_registry.register_boundary(prefix, boundary)
    
    # Add middleware to enforce boundaries on all routes in this router
    @router.middleware("http")
    async def boundary_middleware(request: Request, call_next):
        route_path = request.url.path
        user_permissions = getattr(request.state, "user_permissions", [])
        
        # Validate route access
        if not route_validator.validate_route_access(request, route_path, user_permissions):
            return HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this route"
            )
        
        response = await call_next(request)
        return response
    
    return router


def get_route_boundaries() -> Dict[str, Dict[str, Any]]:
    """Get all registered route boundaries for documentation/debugging."""
    boundaries = {}
    for prefix, boundary in route_registry.boundaries.items():
        boundaries[prefix] = {
            "scope": boundary.scope,
            "allowed_methods": list(boundary.allowed_methods),
            "rate_limit": boundary.rate_limit,
            "required_permissions": boundary.required_permissions,
            "content_type_restrictions": boundary.content_type_restrictions
        }
    return boundaries