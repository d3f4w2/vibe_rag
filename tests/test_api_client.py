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
    monkeypatch.setattr("src.infra.api_client.load_dotenv_if_present", lambda *args, **kwargs: None)
    monkeypatch.setenv("EMBEDDING_API_BASE_URL", "https://example.com/v1")
    monkeypatch.setenv("EMBEDDING_API_KEY", "test-key")
    monkeypatch.setenv("EMBEDDING_MODEL", "test-model")
    return ApiClient()


@pytest.fixture
def api_client_with_dual_provider_env(monkeypatch: pytest.MonkeyPatch) -> ApiClient:
    monkeypatch.setattr("src.infra.api_client.load_dotenv_if_present", lambda *args, **kwargs: None)
    monkeypatch.setenv("EMBEDDING_API_BASE_URL", "https://embedding.example.com/v1")
    monkeypatch.setenv("EMBEDDING_API_KEY", "embedding-key")
    monkeypatch.setenv("EMBEDDING_MODEL", "embedding-model")

    monkeypatch.setenv("GENERATION_API_BASE_URL", "https://generation.example.com/v1")
    monkeypatch.setenv("GENERATION_API_KEY", "generation-key")
    monkeypatch.setenv("GENERATION_MODEL", "generation-model")
    return ApiClient()


def _response(status_code: int, body: dict[str, Any] | None = None) -> httpx.Response:
    request = httpx.Request("POST", "https://example.com/v1/embeddings")
    return httpx.Response(status_code, json=body or {}, request=request)


def _response_for(url: str, status_code: int, body: dict[str, Any] | None = None) -> httpx.Response:
    request = httpx.Request("POST", url)
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


def test_embed_texts_uses_embedding_provider_config(
    api_client_with_dual_provider_env: ApiClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_post(
        self: httpx.Client,
        url: str,
        *,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        captured["url"] = url
        captured["json"] = json
        captured["headers"] = headers
        return _response_for(
            url,
            200,
            {"data": [{"embedding": [0.1, 0.2, 0.3]}]},
        )

    monkeypatch.setattr(httpx.Client, "post", fake_post)

    vectors = api_client_with_dual_provider_env.embed_texts(["embed me"])

    assert vectors == [[0.1, 0.2, 0.3]]
    assert captured["url"] == "https://embedding.example.com/v1/embeddings"
    assert captured["json"]["model"] == "embedding-model"
    assert captured["headers"]["Authorization"] == "Bearer embedding-key"


def test_generate_reasoning_uses_generation_provider_config(
    api_client_with_dual_provider_env: ApiClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_post(
        self: httpx.Client,
        url: str,
        *,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        captured["url"] = url
        captured["json"] = json
        captured["headers"] = headers
        return _response_for(
            url,
            200,
            {"choices": [{"message": {"content": "ok"}}]},
        )

    monkeypatch.setattr(httpx.Client, "post", fake_post)

    text = api_client_with_dual_provider_env.generate_reasoning("hello")

    assert text == "ok"
    assert captured["url"] == "https://generation.example.com/v1/chat/completions"
    assert captured["json"]["model"] == "generation-model"
    assert captured["headers"]["Authorization"] == "Bearer generation-key"


@pytest.mark.parametrize(
    ("missing_var", "expected_error_message"),
    [
        ("GENERATION_API_BASE_URL", "GENERATION_API_BASE_URL"),
        ("GENERATION_API_KEY", "GENERATION_API_KEY"),
    ],
)
def test_generate_reasoning_requires_generation_provider_config(
    missing_var: str,
    expected_error_message: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("src.infra.api_client.load_dotenv_if_present", lambda *args, **kwargs: None)
    monkeypatch.setenv("EMBEDDING_API_BASE_URL", "https://embedding.example.com/v1")
    monkeypatch.setenv("EMBEDDING_API_KEY", "embedding-key")
    monkeypatch.setenv("EMBEDDING_MODEL", "embedding-model")

    monkeypatch.setenv("GENERATION_API_BASE_URL", "https://generation.example.com/v1")
    monkeypatch.setenv("GENERATION_API_KEY", "generation-key")
    monkeypatch.setenv("GENERATION_MODEL", "generation-model")
    monkeypatch.delenv(missing_var, raising=False)

    client = ApiClient()
    with pytest.raises(ValueError, match=expected_error_message):
        client.generate_reasoning("hello")
