#!/usr/bin/env python3
"""
Test script to verify X-User-Id header fallback authentication.
"""

import asyncio
import os
from unittest.mock import AsyncMock, Mock
from fastapi import Request
from jose import jwt

# Add the backend directory to the path so we can import our modules
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from src.api.deps import get_current_user, get_current_user_optional

# Mock environment
os.environ["JWT_SECRET"] = "test-secret-key-for-testing-purposes-only"

async def test_jwt_authentication():
    """Test that JWT authentication still works."""
    print("Testing JWT authentication...")

    # Create a mock JWT token
    test_user_id = "test-user-123"
    token = jwt.encode({"sub": test_user_id}, "test-secret-key-for-testing-purposes-only", algorithm="HS256")

    # Mock request with Authorization header
    mock_request = Mock(spec=Request)
    mock_request.headers = {}

    # Mock credentials
    mock_credentials = Mock()
    mock_credentials.credentials = token

    # Test the dependency
    try:
        result = await get_current_user(mock_request, mock_credentials)
        print(f"✓ JWT authentication successful. User ID: {result}")
        assert result == test_user_id
    except Exception as e:
        print(f"✗ JWT authentication failed: {e}")

async def test_x_userid_fallback():
    """Test that X-User-Id header fallback works."""
    print("Testing X-User-Id header fallback...")

    # Mock request with X-User-Id header but no credentials
    mock_request = Mock(spec=Request)
    mock_request.headers = {"x-user-id": "fallback-user-456"}

    # No credentials (None)
    mock_credentials = None

    # Test the dependency
    try:
        result = await get_current_user(mock_request, mock_credentials)
        print(f"✓ X-User-Id fallback successful. User ID: {result}")
        assert result == "fallback-user-456"
    except Exception as e:
        print(f"✗ X-User-Id fallback failed: {e}")

async def test_both_available():
    """Test that JWT takes precedence when both are available."""
    print("Testing JWT precedence over X-User-Id header...")

    # Create a mock JWT token
    jwt_user_id = "jwt-user-789"
    token = jwt.encode({"sub": jwt_user_id}, "test-secret-key-for-testing-purposes-only", algorithm="HS256")

    # Mock request with both Authorization header and X-User-Id header
    mock_request = Mock(spec=Request)
    mock_request.headers = {"x-user-id": "fallback-user-456"}

    # Mock credentials with JWT
    mock_credentials = Mock()
    mock_credentials.credentials = token

    # Test the dependency
    try:
        result = await get_current_user(mock_request, mock_credentials)
        print(f"✓ JWT precedence successful. User ID: {result}")
        assert result == jwt_user_id  # Should return JWT user ID, not header
    except Exception as e:
        print(f"✗ JWT precedence failed: {e}")

async def test_no_auth():
    """Test that authentication fails when neither JWT nor header is available."""
    print("Testing authentication failure with no auth...")

    # Mock request with no headers
    mock_request = Mock(spec=Request)
    mock_request.headers = {}

    # No credentials (None)
    mock_credentials = None

    # Test the dependency - should raise an exception
    try:
        result = await get_current_user(mock_request, mock_credentials)
        print(f"✗ Expected authentication failure but got user ID: {result}")
    except Exception as e:
        print(f"✓ Authentication correctly failed with no auth: {type(e).__name__}")

async def test_optional_auth():
    """Test optional authentication with X-User-Id header."""
    print("Testing optional authentication with X-User-Id header...")

    # Mock request with X-User-Id header but no credentials
    mock_request = Mock(spec=Request)
    mock_request.headers = {"x-user-id": "optional-user-111"}

    # No credentials (None)
    mock_credentials = None

    # Test the optional dependency
    try:
        result = await get_current_user_optional(mock_request, mock_credentials)
        print(f"✓ Optional auth with X-User-Id successful. User ID: {result}")
        assert result == "optional-user-111"
    except Exception as e:
        print(f"✗ Optional auth with X-User-Id failed: {e}")

async def main():
    print("Starting authentication fallback tests...\n")

    await test_jwt_authentication()
    print()

    await test_x_userid_fallback()
    print()

    await test_both_available()
    print()

    await test_no_auth()
    print()

    await test_optional_auth()
    print()

    print("All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())