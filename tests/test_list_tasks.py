"""Tests for list_tasks functionality."""

from unittest.mock import patch

import pytest


@pytest.mark.asyncio
async def test_list_tasks_with_assignee_only(attio_client, mock_httpx_response):
    """Test listing tasks with assignee filter only."""
    mock_response = {
        "data": [
            {"id": {"task_id": "task-1"}, "deadline_at": "2024-02-10T10:00:00Z"},
            {"id": {"task_id": "task-2"}, "deadline_at": "2024-03-01T12:00:00Z"},
        ]
    }

    with patch.object(attio_client.client, "get") as mock_get:
        mock_get.return_value = mock_httpx_response(json_data=mock_response)

        result = await attio_client.list_tasks(assignee="member-1", limit=2)

        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[0][0] == "/tasks"
        assert call_args[1]["params"]["assignee"] == "member-1"
        assert call_args[1]["params"]["limit"] == 2

        assert result == mock_response


@pytest.mark.asyncio
async def test_list_tasks_with_deadline_start_only(attio_client, mock_httpx_response):
    """Test filtering tasks by deadline start."""
    mock_response = {
        "data": [
            {"id": {"task_id": "task-1"}, "deadline_at": "2024-01-15T00:00:00Z"},
            {"id": {"task_id": "task-2"}, "deadline_at": "2024-02-10T10:00:00Z"},
            {"id": {"task_id": "task-3"}, "deadline_at": None},
        ]
    }

    with patch.object(attio_client.client, "get") as mock_get:
        mock_get.return_value = mock_httpx_response(json_data=mock_response)

        result = await attio_client.list_tasks(deadline_start="2024-02-01", limit=10)

        call_args = mock_get.call_args
        assert call_args[0][0] == "/tasks"
        assert call_args[1]["params"]["limit"] == 500
        assert call_args[1]["params"]["offset"] == 0

        assert len(result["data"]) == 1
        assert result["data"][0]["id"]["task_id"] == "task-2"


@pytest.mark.asyncio
async def test_list_tasks_with_deadline_range(attio_client, mock_httpx_response):
    """Test filtering tasks by deadline range."""
    mock_response = {
        "data": [
            {"id": {"task_id": "task-1"}, "deadline_at": "2024-02-01T00:00:00Z"},
            {"id": {"task_id": "task-2"}, "deadline_at": "2024-02-15T12:00:00Z"},
            {"id": {"task_id": "task-3"}, "deadline_at": "2024-03-01T00:00:00Z"},
        ]
    }

    with patch.object(attio_client.client, "get") as mock_get:
        mock_get.return_value = mock_httpx_response(json_data=mock_response)

        result = await attio_client.list_tasks(
            deadline_start="2024-02-01", deadline_end="2024-02-29", limit=10
        )

        assert len(result["data"]) == 2
        task_ids = [task["id"]["task_id"] for task in result["data"]]
        assert task_ids == ["task-1", "task-2"]


@pytest.mark.asyncio
async def test_list_tasks_with_invalid_deadline_range(attio_client):
    """Test deadline range validation errors."""
    with pytest.raises(ValueError):
        await attio_client.list_tasks(deadline_start="2024-03-01", deadline_end="2024-02-01")
