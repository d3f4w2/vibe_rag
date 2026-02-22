from __future__ import annotations

from typing import Any

import httpx
import pytest

from src.infra.api_client import (
    ApiAuthError,
    ApiClient,
    ApiRateLimitError,
    ApiResponseError,
    ApiTimeoutError,
)


@pytest.fixture
def api_client_with_env(monkeypatch: pytest.MonkeyPatch) -> ApiClient:
    monkeypatch.setenv("EMBEDDING_API_BASE_URL", "https://example.com/v1")
    monkeypatch.setenv("EMBEDDING_API_KEY", "test-key")
    monkeypatch.setenv("EMBEDDING_MODEL", "test-model")
    return ApiClient()


def _response(status_code: int, body: dict[str, Any] | None = None) -> httpx.Response:
    request = httpx.Request("POST", "https://example.com/v1/embeddings")
    return httpx.Response(status_code, json=body or {}, request=request)


def test_embed_texts_maps_timeout_to_api_timeout_error(
    api_client_with_env: ApiClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_post(*args: Any, **kwargs: Any) -> httpx.Response:
        raise httpx.TimeoutException("request timed out")

    monkeypatch.setattr(httpx.Client, "post", fake_post)

    with pytest.raises(ApiTimeoutError):
        api_client_with_env.embed_texts(["sample query"])


@pytest.mark.parametrize(
    ("status_code", "expected_error"),
    [
        (401, ApiAuthError),
        (403, ApiAuthError),
        (429, ApiRateLimitError),
        (500, ApiResponseError),
        (503, ApiResponseError),
    ],
)
def test_embed_texts_maps_http_errors(
    status_code: int,
    expected_error: type[Exception],
    api_client_with_env: ApiClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_post(*args: Any, **kwargs: Any) -> httpx.Response:
        return _response(status_code=status_code, body={"error": "failed"})

    monkeypatch.setattr(httpx.Client, "post", fake_post)

    with pytest.raises(expected_error):
        api_client_with_env.embed_texts(["sample query"])


def test_embed_texts_real_api_smoke() -> None:
    try:
        client = ApiClient()
    except ValueError:
        pytest.skip("embedding env vars are not configured")

    vectors = client.embed_texts(["colposcopy rag smoke test"])

    assert len(vectors) == 1
    assert isinstance(vectors[0], list)
    assert len(vectors[0]) > 0
    assert all(isinstance(value, float) for value in vectors[0])
