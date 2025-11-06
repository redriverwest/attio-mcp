"""Tests for search_companies functionality."""

from unittest.mock import MagicMock, patch

import pytest

from attio_mcp.attio_client import AttioClient


@pytest.mark.asyncio
async def test_search_companies_by_name_only():
    """Test searching companies by name only."""
    mock_response = {
        "data": [
            {
                "id": {"record_id": "company-123"},
                "values": {
                    "name": [{"value": "OpenAI"}],
                    "domains": [{"domain": "openai.com"}],
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

        result = await client.search_companies(query="OpenAI", limit=10)

        # Verify the correct endpoint was called
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "/objects/companies/records/query"

        # Verify the payload
        payload = call_args[1]["json"]
        assert payload["limit"] == 10
        assert payload["filter"]["name"]["$contains"] == "OpenAI"

        # Verify the result
        assert result == mock_response
        assert len(result["data"]) == 1

    await client.close()


@pytest.mark.asyncio
async def test_search_companies_with_domain():
    """Test searching companies with both name and domain for disambiguation."""
    mock_response = {
        "data": [
            {
                "id": {"record_id": "company-456"},
                "values": {
                    "name": [{"value": "Microsoft"}],
                    "domains": [{"domain": "microsoft.com"}],
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

        result = await client.search_companies(query="Microsoft", domain="microsoft.com", limit=5)

        # Verify the correct endpoint was called
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "/objects/companies/records/query"

        # Verify the payload with both filters
        payload = call_args[1]["json"]
        assert payload["limit"] == 5
        assert payload["filter"]["$and"][0]["name"]["$contains"] == "Microsoft"
        assert payload["filter"]["$and"][1]["domains"]["domain"]["$eq"] == "microsoft.com"

        # Verify the result
        assert result == mock_response

    await client.close()


@pytest.mark.asyncio
async def test_search_companies_error_handling():
    """Test error handling when API request fails."""
    client = AttioClient()
    with patch.object(client.client, "post") as mock_post:
        # Create mock response object that raises an error
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = Exception("API error")
        mock_post.return_value = mock_resp

        with pytest.raises(Exception):
            await client.search_companies(query="TestCompany")

    await client.close()
