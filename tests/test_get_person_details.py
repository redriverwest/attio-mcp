"""Tests for get_person_details functionality."""

from unittest.mock import patch

import pytest
from httpx import HTTPStatusError, Request, Response


@pytest.mark.asyncio
async def test_get_person_details_success(attio_client, mock_httpx_response):
    """Test successfully retrieving person details."""
    person_id = "person-abc-123"
    mock_response = {
        "id": {
            "workspace_id": "workspace-123",
            "object_id": "object-456",
            "record_id": person_id,
        },
        "created_at": "2021-12-16T16:16:04.712000000Z",
        "web_url": f"https://app.attio.com/company/{person_id}",
        "values": {
            "name": [{"first_name": "John", "last_name": "Doe", "full_name": "John Doe"}],
            "email_addresses": [{"email_address": "john.doe@example.com", "is_primary": True}],
            "job_title": [{"value": "CEO"}],
            "description": [{"value": "Experienced technology executive"}],
            "phone_numbers": [{"phone_number": "+1234567890", "is_primary": True}],
        },
    }

    with patch.object(attio_client.client, "get") as mock_get:
        mock_get.return_value = mock_httpx_response(json_data=mock_response)

        result = await attio_client.get_person_details(person_id=person_id)

        # Verify the correct endpoint was called
        mock_get.assert_called_once_with(f"/objects/people/records/{person_id}")

        # Verify the result
        assert result == mock_response
        assert result["id"]["record_id"] == person_id
        assert result["values"]["name"][0]["full_name"] == "John Doe"
        assert result["values"]["email_addresses"][0]["email_address"] == "john.doe@example.com"
        assert result["values"]["job_title"][0]["value"] == "CEO"


@pytest.mark.asyncio
async def test_get_person_details_not_found(attio_client, mock_httpx_response):
    """Test handling when person is not found (404)."""
    person_id = "non-existent-id"

    with patch.object(attio_client.client, "get") as mock_get:
        error = HTTPStatusError(
            "404 Not Found",
            request=Request("GET", "http://test.com"),
            response=Response(404),
        )
        mock_get.return_value = mock_httpx_response(
            status_code=404, raise_for_status=error
        )

        with pytest.raises(Exception, match="Person not found"):
            await attio_client.get_person_details(person_id=person_id)


@pytest.mark.asyncio
async def test_get_person_details_api_error(attio_client, mock_httpx_response):
    """Test handling API errors (non-404)."""
    person_id = "test-person-id"

    with patch.object(attio_client.client, "get") as mock_get:
        error = HTTPStatusError(
            "500 Internal Server Error",
            request=Request("GET", "http://test.com"),
            response=Response(500),
        )
        mock_get.return_value = mock_httpx_response(
            status_code=500, raise_for_status=error
        )

        with pytest.raises(Exception, match="Attio API error"):
            await attio_client.get_person_details(person_id=person_id)


@pytest.mark.asyncio
async def test_get_person_details_with_full_record(attio_client, mock_httpx_response):
    """Test retrieving a person with a comprehensive record structure."""
    person_id = "test-full-record-id"
    mock_response = {
        "id": {
            "workspace_id": "workspace-123",
            "object_id": "object-456",
            "record_id": person_id,
        },
        "created_at": "2021-12-16T16:16:04.712000000Z",
        "web_url": f"https://app.attio.com/person/{person_id}",
        "values": {
            "name": [
                {
                    "first_name": "Jane",
                    "last_name": "Smith",
                    "full_name": "Jane Smith",
                }
            ],
            "email_addresses": [{"email_address": "jane@example.com", "is_primary": True}],
            "job_title": [{"value": "CTO"}],
            "description": [{"value": "Technical leader and innovator"}],
            "phone_numbers": [{"phone_number": "+9876543210", "is_primary": True}],
            "linkedin": [{"value": "https://linkedin.com/in/janesmith"}],
            "twitter": [{"value": "https://twitter.com/janesmith"}],
            "primary_location": [
                {
                    "locality": "San Francisco",
                    "region": "California",
                    "country_code": "US",
                }
            ],
        },
    }

    with patch.object(attio_client.client, "get") as mock_get:
        mock_get.return_value = mock_httpx_response(json_data=mock_response)

        result = await attio_client.get_person_details(person_id=person_id)

        # Verify comprehensive data is returned
        assert result["values"]["name"][0]["full_name"] == "Jane Smith"
        assert result["values"]["job_title"][0]["value"] == "CTO"
        assert result["values"]["primary_location"][0]["locality"] == "San Francisco"
        assert result["values"]["linkedin"][0]["value"] == "https://linkedin.com/in/janesmith"
