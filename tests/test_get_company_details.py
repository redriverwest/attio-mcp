"""Tests for get_company_details functionality."""

from unittest.mock import MagicMock, patch

import pytest

from attio_mcp.attio_client import AttioClient


@pytest.mark.asyncio
async def test_get_company_details_success():
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

    client = AttioClient()
    with patch.object(client.client, "get") as mock_get:
        # Create mock response object
        mock_resp = MagicMock()
        mock_resp.json.return_value = mock_response
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        result = await client.get_company_details(company_id=company_id)

        # Verify the correct endpoint was called
        mock_get.assert_called_once_with(f"/objects/companies/records/{company_id}")

        # Verify the result
        assert result == mock_response
        assert result["id"]["record_id"] == company_id
        assert result["values"]["name"][0]["value"] == "Webex"
        assert result["values"]["domains"][0]["domain"] == "webex.com"

    await client.close()


@pytest.mark.asyncio
async def test_get_company_details_not_found():
    """Test handling when company is not found (404)."""
    company_id = "non-existent-id"

    client = AttioClient()
    with patch.object(client.client, "get") as mock_get:
        # Create mock response that raises 404
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_resp.text = "Company not found"

        from httpx import HTTPStatusError, Request, Response

        mock_get.return_value = mock_resp
        mock_resp.raise_for_status.side_effect = HTTPStatusError(
            "404 Not Found",
            request=Request("GET", "http://test.com"),
            response=Response(404),
        )

        with pytest.raises(Exception, match="Company not found"):
            await client.get_company_details(company_id=company_id)

    await client.close()


@pytest.mark.asyncio
async def test_get_company_details_api_error():
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
            await client.get_company_details(company_id=company_id)

    await client.close()


@pytest.mark.asyncio
async def test_get_company_details_with_full_record():
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

    client = AttioClient()
    with patch.object(client.client, "get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.json.return_value = mock_response
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        result = await client.get_company_details(company_id=company_id)

        # Verify comprehensive data is returned
        assert result["values"]["name"][0]["value"] == "Test Company"
        assert len(result["values"]["categories"]) == 2
        assert result["values"]["primary_location"][0]["locality"] == "San Francisco"
        assert result["values"]["employee_range"][0]["option"]["title"] == "50-100"

    await client.close()
