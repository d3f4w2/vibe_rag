from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import uuid4

import httpx
import pytest

from src.cli.main import main
from src.infra.api_client import ApiClient, ApiTimeoutError
from src.reasoning.tendency_service import infer_tendency


class _TimeoutRetriever:
    def retrieve(self, query_text: str, *, top_k: int) -> list[dict[str, object]]:
        del query_text, top_k
        raise ApiTimeoutError("request timed out")


class _EmptyRetriever:
    def retrieve(self, query_text: str, *, top_k: int) -> list[dict[str, object]]:
        del query_text, top_k
        return []


def _workspace_tmp_file(name: str) -> Path:
    base_dir = Path("pytest_tmp_manual") / "step09_failure_paths" / uuid4().hex
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir / name


def _response(status_code: int, body: dict[str, Any] | None = None) -> httpx.Response:
    request = httpx.Request("POST", "https://example.com/v1/embeddings")
    return httpx.Response(status_code, json=body or {}, request=request)


def test_failure_missing_required_stain_input_returns_argument_error(capsys) -> None:
    exit_code = main(
        ["--top-k", "5"],
        retriever_factory=lambda: _EmptyRetriever(),
        tendency_fn=infer_tendency,
    )

    assert exit_code == 2
    captured = capsys.readouterr()
    assert "argument error" in captured.err.lower()


def test_failure_api_timeout_returns_runtime_error(capsys) -> None:
    exit_code = main(
        ["--stain-text", "query text", "--top-k", "5"],
        retriever_factory=lambda: _TimeoutRetriever(),
        tendency_fn=infer_tendency,
    )

    assert exit_code == 1
    captured = capsys.readouterr()
    assert "runtime error" in captured.err.lower()
    assert "timed out" in captured.err.lower()


def test_failure_empty_recall_returns_uncertain_instead_of_crash(capsys) -> None:
    exit_code = main(
        ["--stain-text", "query text", "--top-k", "5"],
        retriever_factory=lambda: _EmptyRetriever(),
        tendency_fn=infer_tendency,
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["tendency"] == "Uncertain"
    assert payload["similar_cases"] == []


def test_failure_invalid_utf8_stain_file_returns_argument_error(capsys) -> None:
    stain_file = _workspace_tmp_file("invalid-utf8.txt")
    stain_file.write_bytes(b"\xff\xfe\xfd")

    exit_code = main(
        ["--stain-file", str(stain_file), "--top-k", "5"],
        retriever_factory=lambda: _EmptyRetriever(),
        tendency_fn=infer_tendency,
    )

    assert exit_code == 2
    captured = capsys.readouterr()
    assert "utf-8" in captured.err.lower()
    assert "stain-file" in captured.err.lower()


def test_failure_api_client_retry_is_observable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("src.infra.api_client.load_dotenv_if_present", lambda *args, **kwargs: None)
    monkeypatch.setenv("EMBEDDING_API_BASE_URL", "https://example.com/v1")
    monkeypatch.setenv("EMBEDDING_API_KEY", "test-key")
    monkeypatch.setenv("EMBEDDING_MODEL", "test-model")

    client = ApiClient(max_retries=2, timeout_sec=1.0)
    attempts = {"count": 0}

    def fake_post(
        self: httpx.Client,
        url: str,
        *,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        del self, url, json, headers
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise httpx.TimeoutException("timeout once")
        return _response(
            200,
            {"data": [{"embedding": [0.12, 0.34, 0.56]}]},
        )

    monkeypatch.setattr(httpx.Client, "post", fake_post)

    vectors = client.embed_texts(["hello"])

    assert attempts["count"] == 2
    assert vectors == [[0.12, 0.34, 0.56]]
