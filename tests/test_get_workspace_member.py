"""Tests for get_workspace_member functionality."""

from unittest.mock import patch

import pytest
from httpx import HTTPStatusError, Request, Response


@pytest.mark.asyncio
async def test_get_workspace_member_success(attio_client, mock_httpx_response):
    """Test successfully retrieving workspace member details."""
    member_id = "82cfb7fc-f667-467d-97db-f5459047eeb6"
    mock_response = {
        "data": {
            "id": {
                "workspace_id": "9135ef71-5324-4eca-a119-a42604411555",
                "workspace_member_id": member_id,
            },
            "first_name": "John",
            "last_name": "Doe",
            "email_address": "john.doe@example.com",
            "avatar_url": "https://lh3.googleusercontent.com/a-/example123",
            "access_level": "admin",
            "created_at": "2023-01-15T10:30:00.000000000Z",
        }
    }

    with patch.object(attio_client.client, "get") as mock_get:
        mock_get.return_value = mock_httpx_response(json_data=mock_response)

        result = await attio_client.get_workspace_member(member_id=member_id)

        # Verify the correct endpoint was called
        mock_get.assert_called_once_with(f"/workspace_members/{member_id}")

        # Verify the result
        assert result == mock_response
        assert result["data"]["first_name"] == "John"
        assert result["data"]["last_name"] == "Doe"
        assert result["data"]["email_address"] == "john.doe@example.com"


@pytest.mark.asyncio
async def test_get_workspace_member_not_found(attio_client, mock_httpx_response):
    """Test handling when workspace member is not found (404)."""
    member_id = "non-existent-member-id"

    with patch.object(attio_client.client, "get") as mock_get:
        error = HTTPStatusError(
            "404 Not Found",
            request=Request("GET", "http://test.com"),
            response=Response(404),
        )
        mock_get.return_value = mock_httpx_response(status_code=404, raise_for_status=error)

        with pytest.raises(Exception, match="Workspace member not found"):
            await attio_client.get_workspace_member(member_id=member_id)


@pytest.mark.asyncio
async def test_get_workspace_member_api_error(attio_client, mock_httpx_response):
    """Test handling API errors (non-404)."""
    member_id = "test-member-id"

    with patch.object(attio_client.client, "get") as mock_get:
        error = HTTPStatusError(
            "500 Internal Server Error",
            request=Request("GET", "http://test.com"),
            response=Response(500),
        )
        mock_get.return_value = mock_httpx_response(status_code=500, raise_for_status=error)

        with pytest.raises(Exception, match="Attio API error"):
            await attio_client.get_workspace_member(member_id=member_id)


@pytest.mark.asyncio
async def test_get_workspace_member_with_null_fields(attio_client, mock_httpx_response):
    """Test handling response with null/optional fields."""
    member_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    mock_response = {
        "data": {
            "id": {
                "workspace_id": "9135ef71-5324-4eca-a119-a42604411555",
                "workspace_member_id": member_id,
            },
            "first_name": "Alex",
            "last_name": None,
            "email_address": "alex@example.com",
            "avatar_url": None,
            "access_level": "member",
            "created_at": "2025-01-01T00:00:00.000000000Z",
        }
    }

    with patch.object(attio_client.client, "get") as mock_get:
        mock_get.return_value = mock_httpx_response(json_data=mock_response)

        result = await attio_client.get_workspace_member(member_id=member_id)

        assert result["data"]["first_name"] == "Alex"
        assert result["data"]["last_name"] is None
        assert result["data"]["avatar_url"] is None
        assert result["data"]["access_level"] == "member"
