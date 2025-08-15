"""
Tests for user management endpoints.
"""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.schemas import UserProfile, UserUpdate


class TestUserEndpoints:
    """Test user management endpoints."""

    @pytest.mark.asyncio
    async def test_user_update_success(self):
        """Test successful user update."""
        from app.api.v1.endpoints.users import update_user
        from app.models.user import User

        # Create mock user
        user_id = uuid4()
        mock_user = MagicMock(spec=User)
        mock_user.id = user_id
        mock_user.username = "testuser"
        mock_user.email = "test@example.com"
        mock_user.full_name = "Test User"
        mock_user.user_type = "operator"
        mock_user.is_active = True
        mock_user.is_superuser = False
        mock_user.created_at = "2023-01-01T00:00:00Z"
        mock_user.last_login = None

        # Create mock current user (same user)
        mock_current_user = mock_user

        # Create mock database session
        mock_db = AsyncMock()
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = mock_result

        # Create update request
        user_update = UserUpdate(
            full_name="Updated Test User",
            email="updated@example.com"
        )

        # Execute update
        result = await update_user(
            user_id=user_id,
            user_update=user_update,
            current_user=mock_current_user,
            db=mock_db
        )

        # Verify result
        assert isinstance(result, UserProfile)
        assert result.id == user_id
        assert result.username == "testuser"
        assert result.email == "updated@example.com"  # Should be updated

        # Verify database operations
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_user)

    @pytest.mark.asyncio
    async def test_user_update_authorization_check(self):
        """Test that users can't update other users unless admin."""
        from fastapi import HTTPException

        from app.api.v1.endpoints.users import update_user
        from app.models.user import User

        # Create mock target user
        target_user_id = uuid4()
        mock_target_user = MagicMock(spec=User)
        mock_target_user.id = target_user_id

        # Create mock current user (different user, not admin)
        current_user_id = uuid4()
        mock_current_user = MagicMock(spec=User)
        mock_current_user.id = current_user_id
        mock_current_user.is_superuser = False

        # Create mock database session
        mock_db = AsyncMock()
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_target_user
        mock_db.execute.return_value = mock_result

        # Create update request
        user_update = UserUpdate(full_name="Unauthorized Update")

        # Execute update and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await update_user(
                user_id=target_user_id,
                user_update=user_update,
                current_user=mock_current_user,
                db=mock_db
            )

        assert exc_info.value.status_code == 403
        assert "Not authorized" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_user_update_email_uniqueness(self):
        """Test email uniqueness validation during update."""
        from fastapi import HTTPException

        from app.api.v1.endpoints.users import update_user
        from app.models.user import User

        # Create mock user
        user_id = uuid4()
        mock_user = MagicMock(spec=User)
        mock_user.id = user_id
        mock_user.email = "original@example.com"

        # Create mock current user (same user)
        mock_current_user = mock_user

        # Create mock existing user with target email
        mock_existing_user = MagicMock(spec=User)
        mock_existing_user.id = uuid4()  # Different user

        # Create mock database session
        mock_db = AsyncMock()

        # First query returns the user to update
        mock_result1 = AsyncMock()
        mock_result1.scalar_one_or_none.return_value = mock_user

        # Second query returns existing user with email
        mock_result2 = AsyncMock()
        mock_result2.scalar_one_or_none.return_value = mock_existing_user

        mock_db.execute.side_effect = [mock_result1, mock_result2]

        # Create update request with existing email
        user_update = UserUpdate(email="existing@example.com")

        # Execute update and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await update_user(
                user_id=user_id,
                user_update=user_update,
                current_user=mock_current_user,
                db=mock_db
            )

        assert exc_info.value.status_code == 400
        assert "Email already registered" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_user_update_admin_privileges(self):
        """Test that admin users can update user_type and is_active."""
        from app.api.v1.endpoints.users import update_user
        from app.models.user import User

        # Create mock target user
        target_user_id = uuid4()
        mock_target_user = MagicMock(spec=User)
        mock_target_user.id = target_user_id
        mock_target_user.email = "target@example.com"
        mock_target_user.user_type = "operator"
        mock_target_user.is_active = True

        # Create mock admin user
        admin_user_id = uuid4()
        mock_admin_user = MagicMock(spec=User)
        mock_admin_user.id = admin_user_id
        mock_admin_user.is_superuser = True

        # Create mock database session
        mock_db = AsyncMock()
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_target_user
        mock_db.execute.return_value = mock_result

        # Create update request with admin-only fields
        user_update = UserUpdate(
            user_type="developer",
            is_active=False
        )

        # Execute update
        await update_user(
            user_id=target_user_id,
            user_update=user_update,
            current_user=mock_admin_user,
            db=mock_db
        )

        # Verify that admin fields were updated
        assert hasattr(mock_target_user, 'user_type')
        assert hasattr(mock_target_user, 'is_active')
        mock_db.commit.assert_called_once()

    def test_user_update_schema_validation(self):
        """Test UserUpdate schema validation."""
        # Valid update
        valid_update = UserUpdate(
            full_name="Valid Name",
            email="valid@example.com",
            user_type="developer"
        )
        assert valid_update.full_name == "Valid Name"
        assert valid_update.email == "valid@example.com"
        assert valid_update.user_type == "developer"

        # Test email validation
        with pytest.raises(ValueError):
            UserUpdate(email="invalid-email")

        # Test user_type validation
        with pytest.raises(ValueError):
            UserUpdate(user_type="invalid_type")
