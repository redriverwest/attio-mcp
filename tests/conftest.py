"""Shared pytest fixtures for attio-mcp tests."""

from typing import Any
from unittest.mock import MagicMock

import pytest

from attio_mcp.attio_client import AttioClient


@pytest.fixture
async def attio_client():
    """Create and cleanup an AttioClient instance."""
    client = AttioClient()
    yield client
    await client.close()


def _create_mock_response(
    json_data: dict[str, Any] | None = None,
    status_code: int = 200,
    raise_for_status: Exception | None = None,
) -> MagicMock:
    """
    Create a mock httpx response object.

    Args:
        json_data: Data to return from response.json()
        status_code: HTTP status code
        raise_for_status: Exception to raise when raise_for_status() is called

    Returns:
        MagicMock configured as an httpx response
    """
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.json.return_value = json_data

    if raise_for_status:
        mock_resp.raise_for_status.side_effect = raise_for_status
    else:
        mock_resp.raise_for_status.return_value = None

    return mock_resp


@pytest.fixture
def mock_httpx_response():
    """Fixture that returns the mock response factory function."""
    return _create_mock_response
