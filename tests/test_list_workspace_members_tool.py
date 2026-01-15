"""Tests for list_workspace_members MCP tool."""

import json
from unittest.mock import patch

import pytest

from attio_mcp.server import list_workspace_members


@pytest.fixture
def mock_workspace_members():
    return {
        "data": [
            {
                "id": {"workspace_member_id": "m1", "workspace_id": "w1"},
                "first_name": "Alice",
                "last_name": "Example",
                "email_address": "alice@example.com",
            },
            {
                "id": {"workspace_member_id": "m2", "workspace_id": "w1"},
                "first_name": "Bob",
                "last_name": "Example",
                "email_address": "bob@example.com",
            },
        ]
    }


@pytest.mark.asyncio
async def test_list_workspace_members_default(mock_workspace_members):
    with patch("attio_mcp.server.attio_client.list_workspace_members") as mock_list:
        mock_list.return_value = mock_workspace_members

        result = await list_workspace_members()
        data = json.loads(result)

        assert "data" in data
        assert len(data["data"]) == 2


@pytest.mark.asyncio
async def test_list_workspace_members_limit(mock_workspace_members):
    with patch("attio_mcp.server.attio_client.list_workspace_members") as mock_list:
        mock_list.return_value = mock_workspace_members

        result = await list_workspace_members(limit=1)
        data = json.loads(result)

        assert len(data["data"]) == 1
        assert data["data"][0]["id"]["workspace_member_id"] == "m1"


@pytest.mark.asyncio
async def test_list_workspace_members_contains_matches_name(mock_workspace_members):
    with patch("attio_mcp.server.attio_client.list_workspace_members") as mock_list:
        mock_list.return_value = mock_workspace_members

        result = await list_workspace_members(contains="bob")
        data = json.loads(result)

        assert len(data["data"]) == 1
        assert data["data"][0]["email_address"] == "bob@example.com"


@pytest.mark.asyncio
async def test_list_workspace_members_contains_matches_email(mock_workspace_members):
    with patch("attio_mcp.server.attio_client.list_workspace_members") as mock_list:
        mock_list.return_value = mock_workspace_members

        result = await list_workspace_members(contains="ALICE@")
        data = json.loads(result)

        assert len(data["data"]) == 1
        assert data["data"][0]["email_address"] == "alice@example.com"


@pytest.mark.asyncio
async def test_list_workspace_members_invalid_limit(mock_workspace_members):
    with patch("attio_mcp.server.attio_client.list_workspace_members") as mock_list:
        mock_list.return_value = mock_workspace_members

        result = await list_workspace_members(limit=-1)
        assert result.startswith("Error:")
