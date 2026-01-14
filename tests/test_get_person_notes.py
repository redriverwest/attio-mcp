"""Tests for get_person_notes functionality."""

from unittest.mock import patch

import pytest
from httpx import HTTPStatusError, Request, Response


@pytest.mark.asyncio
async def test_get_person_notes_success(attio_client, mock_httpx_response):
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

    with patch.object(attio_client.client, "get") as mock_get:
        mock_get.return_value = mock_httpx_response(json_data=mock_response)

        result = await attio_client.get_person_notes(person_id=person_id)

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


@pytest.mark.asyncio
async def test_get_person_notes_empty(attio_client, mock_httpx_response):
    """Test retrieving person with no notes."""
    person_id = "test-person-id"
    mock_response = {"data": []}

    with patch.object(attio_client.client, "get") as mock_get:
        mock_get.return_value = mock_httpx_response(json_data=mock_response)

        result = await attio_client.get_person_notes(person_id=person_id)

        # Verify the result
        assert result == mock_response
        assert len(result["data"]) == 0


@pytest.mark.asyncio
async def test_get_person_notes_not_found(attio_client, mock_httpx_response):
    """Test handling when person is not found (404) - should return empty list."""
    person_id = "non-existent-id"

    with patch.object(attio_client.client, "get") as mock_get:
        error = HTTPStatusError(
            "404 Not Found",
            request=Request("GET", "http://test.com"),
            response=Response(404),
        )
        mock_get.return_value = mock_httpx_response(status_code=404, raise_for_status=error)

        result = await attio_client.get_person_notes(person_id=person_id)

        # For notes, 404 should return empty list, not raise an error
        assert result == {"data": []}


@pytest.mark.asyncio
async def test_get_person_notes_api_error(attio_client, mock_httpx_response):
    """Test handling API errors (non-404)."""
    person_id = "test-person-id"

    with patch.object(attio_client.client, "get") as mock_get:
        error = HTTPStatusError(
            "500 Internal Server Error",
            request=Request("GET", "http://test.com"),
            response=Response(500),
        )
        mock_get.return_value = mock_httpx_response(status_code=500, raise_for_status=error)

        with pytest.raises(Exception, match="Attio API error"):
            await attio_client.get_person_notes(person_id=person_id)


@pytest.mark.asyncio
async def test_get_person_notes_with_multiple_fields(attio_client, mock_httpx_response):
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

    with patch.object(attio_client.client, "get") as mock_get:
        mock_get.return_value = mock_httpx_response(json_data=mock_response)

        result = await attio_client.get_person_notes(person_id=person_id)

        # Verify comprehensive note data
        note = result["data"][0]
        assert note["title"] == "Strategy Discussion"
        assert "growth strategy" in note["content_plaintext"]
        assert "<p>" in note["content_html"]
        assert len(note["mentions"]) == 1
