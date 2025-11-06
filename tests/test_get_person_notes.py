"""Tests for get_person_notes functionality."""

from unittest.mock import MagicMock, patch

import pytest

from attio_mcp.attio_client import AttioClient


@pytest.mark.asyncio
async def test_get_person_notes_success():
    """Test successfully retrieving person notes."""
    person_id = "person-abc-123"
    mock_response = {
        "data": [
            {
                "id": {
                    "record_id": "note-123",
                    "parent_object": "people",
                    "parent_record_id": person_id,
                },
                "title": "Initial Meeting",
                "content_plaintext": "Met with Jane to discuss partnership opportunities.",
                "content_html": "<p>Met with Jane to discuss partnership opportunities.</p>",
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
                    "parent_object": "people",
                    "parent_record_id": person_id,
                },
                "title": "Follow-up Call",
                "content_plaintext": "Discussed technical requirements and timeline.",
                "content_html": "<p>Discussed technical requirements and timeline.</p>",
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

        result = await client.get_person_notes(person_id=person_id)

        # Verify the correct endpoint was called
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[0][0] == "/notes"

        # Verify the parameters
        params = call_args[1]["params"]
        assert params["parent_object"] == "people"
        assert params["parent_record_id"] == person_id

        # Verify the result
        assert result == mock_response
        assert len(result["data"]) == 2
        assert result["data"][0]["title"] == "Initial Meeting"
        assert result["data"][1]["title"] == "Follow-up Call"

    await client.close()


@pytest.mark.asyncio
async def test_get_person_notes_empty():
    """Test retrieving person with no notes."""
    person_id = "test-person-id"
    mock_response = {"data": []}

    client = AttioClient()
    with patch.object(client.client, "get") as mock_get:
        # Create mock response object
        mock_resp = MagicMock()
        mock_resp.json.return_value = mock_response
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        result = await client.get_person_notes(person_id=person_id)

        # Verify the result
        assert result == mock_response
        assert len(result["data"]) == 0

    await client.close()


@pytest.mark.asyncio
async def test_get_person_notes_not_found():
    """Test handling when person is not found (404) - should return empty list."""
    person_id = "non-existent-id"

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

        result = await client.get_person_notes(person_id=person_id)

        # For notes, 404 should return empty list, not raise an error
        assert result == {"data": []}

    await client.close()


@pytest.mark.asyncio
async def test_get_person_notes_api_error():
    """Test handling API errors (non-404)."""
    person_id = "test-person-id"

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
            await client.get_person_notes(person_id=person_id)

    await client.close()


@pytest.mark.asyncio
async def test_get_person_notes_with_multiple_fields():
    """Test retrieving notes with various content types."""
    person_id = "test-person-id"
    mock_response = {
        "data": [
            {
                "id": {
                    "record_id": "note-001",
                    "parent_object": "people",
                    "parent_record_id": person_id,
                },
                "title": "Strategy Discussion",
                "content_plaintext": "Talked about growth strategy and market positioning.",
                "content_html": "<p>Talked about growth strategy and market positioning.</p>",
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

        result = await client.get_person_notes(person_id=person_id)

        # Verify comprehensive note data
        note = result["data"][0]
        assert note["title"] == "Strategy Discussion"
        assert "growth strategy" in note["content_plaintext"]
        assert "<p>" in note["content_html"]
        assert len(note["mentions"]) == 1

    await client.close()
