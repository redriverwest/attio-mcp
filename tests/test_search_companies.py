"""Tests for search_companies functionality."""

from unittest.mock import patch

import pytest


@pytest.mark.asyncio
async def test_search_companies_by_name_only(attio_client, mock_httpx_response):
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

    with patch.object(attio_client.client, "post") as mock_post:
        mock_post.return_value = mock_httpx_response(json_data=mock_response)

        result = await attio_client.search_companies(query="OpenAI", limit=10)

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


@pytest.mark.asyncio
async def test_search_companies_with_domain(attio_client, mock_httpx_response):
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

    with patch.object(attio_client.client, "post") as mock_post:
        mock_post.return_value = mock_httpx_response(json_data=mock_response)

        result = await attio_client.search_companies(
            query="Microsoft", domain="microsoft.com", limit=5
        )

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


@pytest.mark.asyncio
async def test_search_companies_error_handling(attio_client, mock_httpx_response):
    """Test error handling when API request fails."""
    with patch.object(attio_client.client, "post") as mock_post:
        mock_post.return_value = mock_httpx_response(raise_for_status=Exception("API error"))

        with pytest.raises(Exception):
            await attio_client.search_companies(query="TestCompany")
