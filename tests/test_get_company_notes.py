"""Tests for get_company_notes functionality."""

from unittest.mock import MagicMock, patch

import pytest

from attio_mcp.attio_client import AttioClient


@pytest.mark.asyncio
async def test_get_company_notes_success():
    """Test successfully retrieving company notes."""
    company_id = "0000f69b-511f-4321-ac32-3e4c2c93894c"
    mock_response = {
        "data": [
            {
                "id": {
                    "record_id": "note-123",
                    "parent_object": "companies",
                    "parent_record_id": company_id,
                },
                "title": "Discussion with CEO",
                "content_plaintext": "Discussed partnership opportunities.",
                "content_html": "Discussed partnership opportunities and technical integration.",
                "created_at": "2024-11-15T10:30:00.000000000Z",
                "created_by": {
                    "type": "workspace-member",
                    "id": "user-456",
                    "name": "John Doe",
                },
                "updated_at": "2024-11-15T10:30:00.000000000Z",
            },
            {
                "id": {
                    "record_id": "note-124",
                    "parent_object": "companies",
                    "parent_record_id": company_id,
                },
                "title": "Q4 Planning Session",
                "content_plaintext": "Review of annual roadmap and budget allocation.",
                "content_html": "<p>Review of annual roadmap and budget allocation.</p>",
                "created_at": "2024-10-20T14:15:00.000000000Z",
                "created_by": {
                    "type": "workspace-member",
                    "id": "user-789",
                    "name": "Jane Smith",
                },
                "updated_at": "2024-10-20T14:15:00.000000000Z",
            },
        ]
    }

    client = AttioClient()
    with patch.object(client.client, "get") as mock_get:
        # Create mock response object
        mock_resp = MagicMock()
        mock_resp.json.return_value = mock_response
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        result = await client.get_company_notes(company_id=company_id)

        # Verify the correct endpoint was called
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[0][0] == "/notes"

        # Verify the parameters
        params = call_args[1]["params"]
        assert params["parent_object"] == "companies"
        assert params["parent_record_id"] == company_id

        # Verify the result
        assert result == mock_response
        assert len(result["data"]) == 2
        assert result["data"][0]["title"] == "Discussion with CEO"
        assert result["data"][1]["title"] == "Q4 Planning Session"

    await client.close()


@pytest.mark.asyncio
async def test_get_company_notes_empty():
    """Test retrieving company with no notes."""
    company_id = "test-company-id"
    mock_response = {"data": []}

    client = AttioClient()
    with patch.object(client.client, "get") as mock_get:
        # Create mock response object
        mock_resp = MagicMock()
        mock_resp.json.return_value = mock_response
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        result = await client.get_company_notes(company_id=company_id)

        # Verify the result
        assert result == mock_response
        assert len(result["data"]) == 0

    await client.close()


@pytest.mark.asyncio
async def test_get_company_notes_not_found():
    """Test handling when company is not found (404) - should return empty list."""
    company_id = "non-existent-id"

    client = AttioClient()
    with patch.object(client.client, "get") as mock_get:
        # Create mock response that raises 404
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_resp.text = "Not Found"

        from httpx import HTTPStatusError, Request, Response

        mock_get.return_value = mock_resp
        mock_resp.raise_for_status.side_effect = HTTPStatusError(
            "404 Not Found",
            request=Request("GET", "http://test.com"),
            response=Response(404),
        )

        result = await client.get_company_notes(company_id=company_id)

        # For notes, 404 should return empty list, not raise an error
        assert result == {"data": []}

    await client.close()


@pytest.mark.asyncio
async def test_get_company_notes_api_error():
    """Test handling API errors (non-404)."""
    company_id = "test-company-id"

    client = AttioClient()
    with patch.object(client.client, "get") as mock_get:
        # Create mock response that raises 500
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.text = "Internal Server Error"

        from httpx import HTTPStatusError, Request, Response

        mock_get.return_value = mock_resp
        mock_resp.raise_for_status.side_effect = HTTPStatusError(
            "500 Internal Server Error",
            request=Request("GET", "http://test.com"),
            response=Response(500),
        )

        with pytest.raises(Exception, match="Attio API error"):
            await client.get_company_notes(company_id=company_id)

    await client.close()


@pytest.mark.asyncio
async def test_get_company_notes_with_multiple_fields():
    """Test retrieving notes with various content types."""
    company_id = "test-company-id"
    mock_response = {
        "data": [
            {
                "id": {
                    "record_id": "note-001",
                    "parent_object": "companies",
                    "parent_record_id": company_id,
                },
                "title": "Technical Review",
                "content_plaintext": "Product architecture is solid. Recommended improvements...",
                "content_html": "<p>Product architecture is solid. Recommended improvements:</p>",
                "created_at": "2024-11-10T09:00:00.000000000Z",
                "created_by": {
                    "type": "workspace-member",
                    "id": "user-123",
                    "name": "Alex Engineer",
                },
                "updated_at": "2024-11-10T09:00:00.000000000Z",
                "mentions": [{"type": "workspace-member", "id": "user-456"}],
            }
        ]
    }

    client = AttioClient()
    with patch.object(client.client, "get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.json.return_value = mock_response
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        result = await client.get_company_notes(company_id=company_id)

        # Verify comprehensive note data
        note = result["data"][0]
        assert note["title"] == "Technical Review"
        assert "caching" in note["content_plaintext"]
        assert "<p>" in note["content_html"]
        assert len(note["mentions"]) == 1

    await client.close()
