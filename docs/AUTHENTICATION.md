# Z2 Authentication & Authorization System

This document describes the comprehensive authentication and authorization system implemented in Phase 6 of the Z2 platform.

## Overview

The Z2 platform now features a robust, production-ready authentication and authorization system that provides:

- **JWT-based authentication** with access and refresh tokens
- **Role-based access control (RBAC)** with granular permissions
- **Database-backed token management** for security and revocation
- **Frontend integration** with React components and context
- **Comprehensive security features** following modern best practices

## Architecture

### Backend Components

1. **Models** (`app/models/role.py`, `app/models/user.py`)
   - `User`: Extended with role relationships
   - `Role`: System roles with permissions
   - `Permission`: Resource-action based permissions
   - `RefreshToken`: Database-backed token storage

2. **Security Module** (`app/core/security.py`)
   - JWT token creation and validation
   - Password hashing and strength validation
   - Refresh token management
   - Rate limiting and security features

3. **Authorization Dependencies** (`app/core/auth_dependencies.py`)
   - FastAPI dependencies for route protection
   - Role and permission checking utilities
   - Convenience decorators and dependencies

4. **Authentication Endpoints** (`app/api/v1/endpoints/auth.py`)
   - User registration and login
   - Token refresh and revocation
   - Current user profile retrieval

### Frontend Components

1. **Authentication Service** (`frontend/src/services/auth.ts`)
   - API integration for auth endpoints
   - Token storage and management
   - Automatic token refresh

2. **Authentication Context** (`frontend/src/hooks/useAuth.tsx`)
   - React context for auth state management
   - Login, logout, and registration functions
   - Error handling and loading states

3. **UI Components**
   - `LoginForm.tsx`: Full-featured login form
   - `RegisterForm.tsx`: User registration form
   - `ProtectedRoute.tsx`: Route protection with role checking
   - `AuthPage.tsx`: Combined auth page

## Role System

### Default Roles

The system includes five predefined roles with hierarchical permissions:

1. **Admin** - Full system access
   - All permissions including system administration
   - User management and system configuration

2. **Manager** - Broad platform management
   - User and system management (no admin functions)
   - Full agent and workflow access

3. **Developer** - Agent and workflow development
   - Create, modify, and execute agents/workflows
   - Limited user access (read-only)

4. **Operator** - Execute workflows and agents
   - Execute existing agents and workflows
   - Read-only access to users and configurations

5. **Viewer** - Read-only access
   - View-only access to all resources
   - No creation, modification, or execution rights

### Permission System

Permissions follow a resource-action pattern:

- **Resources**: `users`, `agents`, `workflows`, `system`
- **Actions**: `read`, `write`, `delete`, `execute`, `admin`, `manage`

Examples:
- `users:read` - View user information
- `agents:execute` - Run agent tasks
- `workflows:write` - Create/modify workflows
- `system:admin` - Full system administration

## Usage Examples

### Backend: Protecting Endpoints

```python
from app.core.auth_dependencies import RequirePermissions, RequireRole

# Require specific permission
@router.get("/users/", dependencies=[Depends(RequirePermissions("users:read"))])
async def list_users():
    pass

# Require role level
@router.delete("/users/{id}", dependencies=[Depends(RequireRole("admin"))])
async def delete_user():
    pass

# Multiple permission options
@router.get("/data", dependencies=[Depends(RequireAnyPermission("admin:read", "user:read"))])
async def get_data():
    pass
```

### Backend: Manual Permission Checking

```python
from app.core.auth_dependencies import get_current_user, check_user_permissions

async def my_endpoint(current_user: User = Depends(get_current_user)):
    if not check_user_permissions(current_user, ["agents:execute"]):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Continue with business logic
```

### Frontend: Using Authentication

```tsx
import { useAuth } from '../hooks/useAuth';

function MyComponent() {
  const { authState, login, logout } = useAuth();
  
  if (!authState.isAuthenticated) {
    return <LoginForm />;
  }
  
  return (
    <div>
      <p>Welcome, {authState.user?.username}!</p>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

### Frontend: Protected Routes

```tsx
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <Routes>
      <Route path="/auth" element={<AuthPage />} />
      
      <Route 
        path="/admin" 
        element={
          <ProtectedRoute requiredRole="admin">
            <AdminPanel />
          </ProtectedRoute>
        } 
      />
    </Routes>
  );
}
```

## Security Features

### Password Security
- Bcrypt hashing with configurable rounds
- Strength validation (length, complexity, special characters)
- Protection against common password attacks

### Token Security
- JWT with expiration and security metadata
- Refresh token rotation and database storage
- Token revocation and blacklisting
- Automatic cleanup of expired tokens

### API Security
- Rate limiting for authentication endpoints
- CORS protection with configurable origins
- Security headers (HSTS, CSP, XSS protection)
- Request validation and sanitization

### Session Management
- Multiple session support per user
- Session tracking and revocation
- Automatic cleanup and maintenance

## Database Schema

### Migration Files
- `b32d1e47ba53_add_roles_permissions_and_refresh_.py` - Core tables
- `c7bb81d27d15_seed_default_roles_and_permissions.py` - Default data

### Key Tables
- `users` - User accounts with role relationships
- `roles` - System roles
- `permissions` - Granular permissions
- `role_permissions` - Role-permission mapping
- `user_roles` - User-role assignments
- `refresh_tokens` - Secure token storage

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout
- `POST /api/v1/auth/refresh` - Token refresh
- `GET /api/v1/auth/me` - Current user profile

### Protected Endpoints
All existing CRUD endpoints now include role-based protection:
- User management requires appropriate `users:*` permissions
- Agent management requires `agents:*` permissions
- Workflow management requires `workflows:*` permissions

## Testing

The system includes comprehensive tests covering:
- Password security and validation
- JWT token creation and verification
- Authentication endpoints
- Authorization dependencies
- Role-based access control
- Refresh token functionality

Run tests with:
```bash
cd backend
python -m pytest tests/test_auth_system.py -v
```

## Configuration

### Environment Variables
- `SECRET_KEY` - JWT signing key (required)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration (default: 30)
- `CORS_ORIGINS` - Allowed frontend origins
- `DATABASE_URL` - Database connection string

### Frontend Configuration
- `VITE_API_URL` - Backend API base URL

## Deployment Considerations

### Production Checklist
- [ ] Set strong SECRET_KEY
- [ ] Configure proper CORS origins
- [ ] Enable HTTPS/TLS
- [ ] Set up proper database security
- [ ] Configure rate limiting
- [ ] Set up monitoring and logging

### Security Best Practices
- Regularly rotate JWT secret keys
- Monitor authentication failures
- Implement proper session management
- Keep dependencies updated
- Use secure communication channels

## Future Enhancements

Potential improvements for future phases:
- Multi-factor authentication (MFA)
- OAuth/SSO integration
- Advanced audit logging
- Password reset functionality
- Account lockout policies
- Advanced permission scoping

## Support

For questions or issues with the authentication system:
1. Check the test files for usage examples
2. Review the API documentation
3. Examine the frontend components for integration patterns
4. Refer to the security module for advanced features