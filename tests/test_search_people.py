"""Tests for search_people functionality."""

from unittest.mock import patch

import pytest


@pytest.mark.asyncio
async def test_search_people_by_name_only(attio_client, mock_httpx_response):
    """Test searching people by name only."""
    mock_response = {
        "data": [
            {
                "id": {"record_id": "person-123"},
                "values": {
                    "name": [{"first_name": "John", "last_name": "Doe", "full_name": "John Doe"}],
                    "email_addresses": [{"email_address": "john.doe@example.com"}],
                },
            }
        ]
    }

    with patch.object(attio_client.client, "post") as mock_post:
        mock_post.return_value = mock_httpx_response(json_data=mock_response)

        result = await attio_client.search_people(query="John", limit=10)

        # Verify the correct endpoint was called
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "/objects/people/records/query"

        # Verify the payload
        payload = call_args[1]["json"]
        assert payload["limit"] == 10
        assert payload["filter"]["name"]["$contains"] == "John"

        # Verify the result
        assert result == mock_response
        assert len(result["data"]) == 1


@pytest.mark.asyncio
async def test_search_people_with_email(attio_client, mock_httpx_response):
    """Test searching people with both name and email for disambiguation."""
    mock_response = {
        "data": [
            {
                "id": {"record_id": "person-456"},
                "values": {
                    "name": [
                        {"first_name": "Jane", "last_name": "Smith", "full_name": "Jane Smith"}
                    ],
                    "email_addresses": [{"email_address": "jane.smith@example.com"}],
                },
            }
        ]
    }

    with patch.object(attio_client.client, "post") as mock_post:
        mock_post.return_value = mock_httpx_response(json_data=mock_response)

        result = await attio_client.search_people(
            query="Jane Smith", email="jane.smith@example.com", limit=5
        )

        # Verify the correct endpoint was called
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "/objects/people/records/query"

        # Verify the payload with both filters
        payload = call_args[1]["json"]
        assert payload["limit"] == 5
        assert payload["filter"]["$and"][0]["name"]["$contains"] == "Jane Smith"
        assert (
            payload["filter"]["$and"][1]["email_addresses"]["email_address"]["$eq"]
            == "jane.smith@example.com"
        )

        # Verify the result
        assert result == mock_response


@pytest.mark.asyncio
async def test_search_people_error_handling(attio_client, mock_httpx_response):
    """Test error handling when API request fails."""
    with patch.object(attio_client.client, "post") as mock_post:
        mock_post.return_value = mock_httpx_response(
            raise_for_status=Exception("API error")
        )

        with pytest.raises(Exception):
            await attio_client.search_people(query="TestPerson")
