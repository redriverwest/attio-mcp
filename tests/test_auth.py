"""Tests for authentication module."""

import pytest

from attio_mcp.auth import BearerTokenVerifier
from attio_mcp.config import settings


def test_bearer_token_verifier_valid_token():
    """Test that a valid token is accepted."""
    verifier = BearerTokenVerifier()

    # Use the configured token if available, otherwise skip test
    if not settings.mcp_bearer_token:
        pytest.skip("MCP_BEARER_TOKEN not configured")

    token = settings.mcp_bearer_token
    result = verifier.verify_token(token)

    assert result is not None
    assert result.token == token
    assert result.client_id == "attio-mcp-client"
    assert result.scopes == ["*"]
    assert result.expires_at is None


def test_bearer_token_verifier_invalid_token():
    """Test that an invalid token is rejected."""
    verifier = BearerTokenVerifier()

    # Skip if no token configured (all tokens would be accepted)
    if not settings.mcp_bearer_token:
        pytest.skip("MCP_BEARER_TOKEN not configured - auth disabled")

    invalid_token = "invalid_token_12345"
    result = verifier.verify_token(invalid_token)

    assert result is None


def test_bearer_token_verifier_empty_token():
    """Test that an empty token is rejected."""
    verifier = BearerTokenVerifier()

    # Skip if no token configured
    if not settings.mcp_bearer_token:
        pytest.skip("MCP_BEARER_TOKEN not configured - auth disabled")

    result = verifier.verify_token("")

    assert result is None


def test_bearer_token_verifier_no_config():
    """Test behavior when no token is configured (auth disabled)."""
    verifier = BearerTokenVerifier()

    # Only run this test if token is NOT configured
    if settings.mcp_bearer_token:
        pytest.skip("MCP_BEARER_TOKEN is configured")

    # When no token is configured, any token should be accepted
    result = verifier.verify_token("any_token")

    assert result is not None
    assert result.client_id == "anonymous"
    assert result.scopes == ["*"]
