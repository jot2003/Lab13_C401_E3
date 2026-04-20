from __future__ import annotations

import re
from unittest.mock import patch

import pytest
from starlette.testclient import TestClient

from app.logging_config import configure_logging
from app.main import app

#run: python -m pytest tests/test_middleware.py -v -s 2>&1 | tee test_middleware.log

configure_logging()


@pytest.fixture()
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


def test_custom_id_in_log_and_response(client: TestClient) -> None:
    """Case 1: custom x-request-id → bind_contextvars called with exact ID, response header matches."""
    custom_id = "my-custom-id-abc123"
    with patch("app.middleware.bind_contextvars") as mock_bind:
        resp = client.get("/health", headers={"x-request-id": custom_id})

    assert resp.status_code == 200
    assert resp.headers["x-request-id"] == custom_id
    mock_bind.assert_called_once_with(correlation_id=custom_id)


def test_generated_id_format_in_log_and_response(client: TestClient) -> None:
    """Case 2: no header → log bound with req-<8hex> ID that matches response header."""
    with patch("app.middleware.bind_contextvars") as mock_bind:
        resp = client.get("/health")

    assert resp.status_code == 200
    resp_id = resp.headers["x-request-id"]
    assert re.match(r"^req-[0-9a-f]{8}$", resp_id), f"Expected req-<8hex>, got: {resp_id}"
    assert resp.headers.get("x-response-time-ms") is not None

    bound_id = mock_bind.call_args.kwargs["correlation_id"]
    assert bound_id == resp_id, f"Log ID '{bound_id}' != response ID '{resp_id}'"


def test_no_context_leak_between_requests(client: TestClient) -> None:
    """Case 3: two consecutive requests produce independent IDs — no context bleed."""
    with patch("app.middleware.bind_contextvars") as mock_bind:
        resp1 = client.get("/health")
        resp2 = client.get("/health")

    id1 = resp1.headers["x-request-id"]
    id2 = resp2.headers["x-request-id"]
    assert id1 != id2, f"Context leaked: both requests returned same ID '{id1}'"

    calls = [c.kwargs["correlation_id"] for c in mock_bind.call_args_list]
    assert id1 in calls, f"ID from request 1 ('{id1}') not bound to context"
    assert id2 in calls, f"ID from request 2 ('{id2}') not bound to context"
