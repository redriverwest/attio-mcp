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

        result = await attio_client.search_companies(name="OpenAI", limit=10)

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
            name="Microsoft", domain="microsoft.com", limit=5
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
async def test_search_companies_with_owner_only(attio_client, mock_httpx_response):
    """Test listing companies by owner only (no name/domain filter)."""
    mock_response = {"data": []}

    with patch.object(attio_client.client, "post") as mock_post:
        mock_post.return_value = mock_httpx_response(json_data=mock_response)

        result = await attio_client.search_companies(name=None, owner_id="member-123", limit=3)

        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "/objects/companies/records/query"

        payload = call_args[1]["json"]
        assert payload["limit"] == 3
        assert payload["filter"]["owner"]["referenced_actor_type"] == "workspace-member"
        assert payload["filter"]["owner"]["referenced_actor_id"] == "member-123"

        assert result == mock_response


@pytest.mark.asyncio
async def test_search_companies_with_reminder_start_only(attio_client, mock_httpx_response):
    """Test searching companies with reminder date lower bound."""
    mock_response = {"data": []}

    with patch.object(attio_client.client, "post") as mock_post:
        mock_post.return_value = mock_httpx_response(json_data=mock_response)

        result = await attio_client.search_companies(reminder_start="2024-01-01", limit=10)

        payload = mock_post.call_args[1]["json"]
        assert payload["filter"]["reminder"]["$gte"] == "2024-01-01"
        assert result == mock_response


@pytest.mark.asyncio
async def test_search_companies_with_reminder_end_only(attio_client, mock_httpx_response):
    """Test searching companies with reminder date upper bound."""
    mock_response = {"data": []}

    with patch.object(attio_client.client, "post") as mock_post:
        mock_post.return_value = mock_httpx_response(json_data=mock_response)

        result = await attio_client.search_companies(reminder_end="2024-12-31", limit=10)

        payload = mock_post.call_args[1]["json"]
        assert payload["filter"]["reminder"]["$lte"] == "2024-12-31"
        assert result == mock_response


@pytest.mark.asyncio
async def test_search_companies_with_reminder_range(attio_client, mock_httpx_response):
    """Test searching companies with reminder date range."""
    mock_response = {"data": []}

    with patch.object(attio_client.client, "post") as mock_post:
        mock_post.return_value = mock_httpx_response(json_data=mock_response)

        result = await attio_client.search_companies(
            reminder_start="2024-01-01", reminder_end="2024-12-31", limit=10
        )

        payload = mock_post.call_args[1]["json"]
        assert payload["filter"]["reminder"]["$gte"] == "2024-01-01"
        assert payload["filter"]["reminder"]["$lte"] == "2024-12-31"
        assert result == mock_response


@pytest.mark.asyncio
async def test_search_companies_with_invalid_reminder_range(attio_client):
    """Test reminder range validation errors."""
    with pytest.raises(ValueError):
        await attio_client.search_companies(reminder_start="2024-12-31", reminder_end="2024-01-01")


@pytest.mark.asyncio
async def test_search_companies_with_owner_and_name(attio_client, mock_httpx_response):
    """Test searching companies by name and owner together."""
    mock_response = {"data": []}

    with patch.object(attio_client.client, "post") as mock_post:
        mock_post.return_value = mock_httpx_response(json_data=mock_response)

        result = await attio_client.search_companies(name="OpenAI", owner_id="member-123", limit=10)

        mock_post.assert_called_once()
        payload = mock_post.call_args[1]["json"]
        assert payload["limit"] == 10
        assert payload["filter"]["$and"][0]["name"]["$contains"] == "OpenAI"
        assert payload["filter"]["$and"][1]["owner"]["referenced_actor_type"] == "workspace-member"
        assert payload["filter"]["$and"][1]["owner"]["referenced_actor_id"] == "member-123"

        assert result == mock_response


@pytest.mark.asyncio
async def test_search_companies_with_owner_domain_and_name(attio_client, mock_httpx_response):
    """Test searching companies by name, domain, and owner together."""
    mock_response = {"data": []}

    with patch.object(attio_client.client, "post") as mock_post:
        mock_post.return_value = mock_httpx_response(json_data=mock_response)

        result = await attio_client.search_companies(
            name="OpenAI", domain="openai.com", owner_id="member-123", limit=10
        )

        mock_post.assert_called_once()
        payload = mock_post.call_args[1]["json"]
        assert payload["limit"] == 10
        assert payload["filter"]["$and"][0]["name"]["$contains"] == "OpenAI"
        assert payload["filter"]["$and"][1]["domains"]["domain"]["$eq"] == "openai.com"
        assert payload["filter"]["$and"][2]["owner"]["referenced_actor_type"] == "workspace-member"
        assert payload["filter"]["$and"][2]["owner"]["referenced_actor_id"] == "member-123"

        assert result == mock_response


@pytest.mark.asyncio
async def test_search_companies_error_handling(attio_client, mock_httpx_response):
    """Test error handling when API request fails."""
    with patch.object(attio_client.client, "post") as mock_post:
        mock_post.return_value = mock_httpx_response(raise_for_status=Exception("API error"))

        with pytest.raises(Exception):
            await attio_client.search_companies(name="TestCompany")
