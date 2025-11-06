"""Tests for search_people functionality."""

from unittest.mock import MagicMock, patch

import pytest

from attio_mcp.attio_client import AttioClient


@pytest.mark.asyncio
async def test_search_people_by_name_only():
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

    client = AttioClient()
    with patch.object(client.client, "post") as mock_post:
        # Create mock response object
        mock_resp = MagicMock()
        mock_resp.json.return_value = mock_response
        mock_resp.raise_for_status.return_value = None
        mock_post.return_value = mock_resp

        result = await client.search_people(query="John", limit=10)

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

    await client.close()


@pytest.mark.asyncio
async def test_search_people_with_email():
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

    client = AttioClient()
    with patch.object(client.client, "post") as mock_post:
        # Create mock response object
        mock_resp = MagicMock()
        mock_resp.json.return_value = mock_response
        mock_resp.raise_for_status.return_value = None
        mock_post.return_value = mock_resp

        result = await client.search_people(
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

    await client.close()


@pytest.mark.asyncio
async def test_search_people_error_handling():
    """Test error handling when API request fails."""
    client = AttioClient()
    with patch.object(client.client, "post") as mock_post:
        # Create mock response object that raises an error
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = Exception("API error")
        mock_post.return_value = mock_resp

        with pytest.raises(Exception):
            await client.search_people(query="TestPerson")

    await client.close()
