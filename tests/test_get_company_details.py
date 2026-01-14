"""Tests for get_company_details functionality."""

from unittest.mock import patch

import pytest
from httpx import HTTPStatusError, Request, Response


@pytest.mark.asyncio
async def test_get_company_details_success(attio_client, mock_httpx_response):
    """Test successfully retrieving company details."""
    company_id = "0000f69b-511f-4321-ac32-3e4c2c93894c"
    mock_response = {
        "id": {
            "workspace_id": "9135ef71-5324-4eca-a119-a42604411555",
            "object_id": "a44c2799-f16a-4765-942e-5a66c95175fc",
            "record_id": company_id,
        },
        "created_at": "2021-12-16T16:16:04.712000000Z",
        "web_url": "https://app.attio.com/red-river-west/company/" + company_id,
        "values": {
            "name": [{"value": "Webex"}],
            "domains": [{"domain": "webex.com", "root_domain": "webex.com"}],
            "description": [{"value": "Webex specializes in video conferencing solutions."}],
            "categories": [{"option": {"title": "Information Technology & Services"}}],
        },
    }

    with patch.object(attio_client.client, "get") as mock_get:
        mock_get.return_value = mock_httpx_response(json_data=mock_response)

        result = await attio_client.get_company_details(company_id=company_id)

        # Verify the correct endpoint was called
        mock_get.assert_called_once_with(f"/objects/companies/records/{company_id}")

        # Verify the result
        assert result == mock_response
        assert result["id"]["record_id"] == company_id
        assert result["values"]["name"][0]["value"] == "Webex"
        assert result["values"]["domains"][0]["domain"] == "webex.com"


@pytest.mark.asyncio
async def test_get_company_details_not_found(attio_client, mock_httpx_response):
    """Test handling when company is not found (404)."""
    company_id = "non-existent-id"

    with patch.object(attio_client.client, "get") as mock_get:
        error = HTTPStatusError(
            "404 Not Found",
            request=Request("GET", "http://test.com"),
            response=Response(404),
        )
        mock_get.return_value = mock_httpx_response(status_code=404, raise_for_status=error)

        with pytest.raises(Exception, match="Company not found"):
            await attio_client.get_company_details(company_id=company_id)


@pytest.mark.asyncio
async def test_get_company_details_api_error(attio_client, mock_httpx_response):
    """Test handling API errors (non-404)."""
    company_id = "test-company-id"

    with patch.object(attio_client.client, "get") as mock_get:
        error = HTTPStatusError(
            "500 Internal Server Error",
            request=Request("GET", "http://test.com"),
            response=Response(500),
        )
        mock_get.return_value = mock_httpx_response(status_code=500, raise_for_status=error)

        with pytest.raises(Exception, match="Attio API error"):
            await attio_client.get_company_details(company_id=company_id)


@pytest.mark.asyncio
async def test_get_company_details_with_full_record(attio_client, mock_httpx_response):
    """Test retrieving a company with a comprehensive record structure."""
    company_id = "test-full-record-id"
    mock_response = {
        "id": {
            "workspace_id": "workspace-123",
            "object_id": "object-456",
            "record_id": company_id,
        },
        "created_at": "2021-12-16T16:16:04.712000000Z",
        "web_url": f"https://app.attio.com/company/{company_id}",
        "values": {
            "name": [{"value": "Test Company"}],
            "domains": [{"domain": "test.com"}],
            "description": [{"value": "A test company"}],
            "categories": [
                {"option": {"title": "Technology"}},
                {"option": {"title": "SAAS"}},
            ],
            "primary_location": [
                {
                    "locality": "San Francisco",
                    "region": "California",
                    "country_code": "US",
                }
            ],
            "employee_range": [{"option": {"title": "50-100"}}],
            "logo_url": [{"value": "https://logo.clearbit.com/test.com"}],
            "twitter": [{"value": "https://twitter.com/testcompany"}],
            "linkedin": [{"value": "https://linkedin.com/company/testcompany"}],
        },
    }

    with patch.object(attio_client.client, "get") as mock_get:
        mock_get.return_value = mock_httpx_response(json_data=mock_response)

        result = await attio_client.get_company_details(company_id=company_id)

        # Verify comprehensive data is returned
        assert result["values"]["name"][0]["value"] == "Test Company"
        assert len(result["values"]["categories"]) == 2
        assert result["values"]["primary_location"][0]["locality"] == "San Francisco"
        assert result["values"]["employee_range"][0]["option"]["title"] == "50-100"
