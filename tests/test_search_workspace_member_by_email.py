"""Tests for search_workspace_member_by_email functionality."""

import json
from unittest.mock import patch

import pytest
from httpx import HTTPStatusError, Request, Response

from attio_mcp.server import search_workspace_member_by_email


@pytest.fixture
def mock_workspace_members():
    """Sample workspace members list matching actual Attio API response format."""
    return {
        "data": [
            {
                "id": {
                    "workspace_id": "9135ef71-5324-4eca-a119-a42604411555",
                    "workspace_member_id": "82cfb7fc-f667-467d-97db-f5459047eeb6",
                },
                "first_name": "John",
                "last_name": "Doe",
                "email_address": "john.doe@example.com",
                "avatar_url": "https://lh3.googleusercontent.com/a-/example123",
                "access_level": "admin",
                "created_at": "2023-01-15T10:30:00.000000000Z",
            },
            {
                "id": {
                    "workspace_id": "9135ef71-5324-4eca-a119-a42604411555",
                    "workspace_member_id": "93d8a2b8-e953-4c1d-bc62-2a57e5e8e481",
                },
                "first_name": "Jane",
                "last_name": "Smith",
                "email_address": "jane.smith@example.com",
                "avatar_url": None,
                "access_level": "member",
                "created_at": "2023-02-20T14:00:00.000000000Z",
            },
        ]
    }


@pytest.mark.asyncio
async def test_list_workspace_members_success(attio_client, mock_httpx_response):
    """Test successfully listing workspace members."""
    mock_response = {
        "data": [
            {
                "id": {
                    "workspace_id": "9135ef71-5324-4eca-a119-a42604411555",
                    "workspace_member_id": "82cfb7fc-f667-467d-97db-f5459047eeb6",
                },
                "first_name": "Test",
                "last_name": "User",
                "email_address": "test@example.com",
                "avatar_url": "https://example.com/avatar.jpg",
                "access_level": "admin",
                "created_at": "2023-01-15T10:30:00.000000000Z",
            }
        ]
    }

    with patch.object(attio_client.client, "get") as mock_get:
        mock_get.return_value = mock_httpx_response(json_data=mock_response)

        result = await attio_client.list_workspace_members()

        mock_get.assert_called_once_with("/workspace_members")
        assert result == mock_response
        assert len(result["data"]) == 1


@pytest.mark.asyncio
async def test_list_workspace_members_api_error(attio_client, mock_httpx_response):
    """Test handling API errors when listing workspace members."""
    with patch.object(attio_client.client, "get") as mock_get:
        error = HTTPStatusError(
            "500 Internal Server Error",
            request=Request("GET", "http://test.com"),
            response=Response(500),
        )
        mock_get.return_value = mock_httpx_response(status_code=500, raise_for_status=error)

        with pytest.raises(Exception, match="Attio API error"):
            await attio_client.list_workspace_members()


@pytest.mark.asyncio
async def test_search_by_email_found(mock_workspace_members):
    """Test finding a workspace member by email."""
    with patch("attio_mcp.server.attio_client.list_workspace_members") as mock_list:
        mock_list.return_value = mock_workspace_members

        result = await search_workspace_member_by_email("john.doe@example.com")
        data = json.loads(result)

        assert "data" in data
        assert data["data"]["first_name"] == "John"
        assert data["data"]["email_address"] == "john.doe@example.com"


@pytest.mark.asyncio
async def test_search_by_email_case_insensitive(mock_workspace_members):
    """Test that email search is case-insensitive."""
    with patch("attio_mcp.server.attio_client.list_workspace_members") as mock_list:
        mock_list.return_value = mock_workspace_members

        result = await search_workspace_member_by_email("JOHN.DOE@EXAMPLE.COM")
        data = json.loads(result)

        assert "data" in data
        assert data["data"]["first_name"] == "John"


@pytest.mark.asyncio
async def test_search_by_email_not_found(mock_workspace_members):
    """Test when email is not found."""
    with patch("attio_mcp.server.attio_client.list_workspace_members") as mock_list:
        mock_list.return_value = mock_workspace_members

        result = await search_workspace_member_by_email("nonexistent@example.com")
        data = json.loads(result)

        assert "error" in data
        assert "No workspace member found" in data["error"]


@pytest.mark.asyncio
async def test_search_by_email_api_error():
    """Test handling API errors during search."""
    with patch("attio_mcp.server.attio_client.list_workspace_members") as mock_list:
        mock_list.side_effect = Exception("Attio API error: 500")

        result = await search_workspace_member_by_email("test@example.com")

        assert result.startswith("Error:")
