from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from src.cli.main import main


class _FakeRetriever:
    def __init__(self, similar_cases: list[dict[str, object]]) -> None:
        self._similar_cases = similar_cases
        self.calls: list[tuple[str, int]] = []

    def retrieve(self, query_text: str, *, top_k: int) -> list[dict[str, object]]:
        self.calls.append((query_text, top_k))
        return self._similar_cases


def _fake_tendency(
    similar_cases: list[dict[str, object]],
    *,
    top_k: int,
) -> dict[str, str]:
    if similar_cases and top_k > 0:
        return {
            "tendency": "HSIL",
            "reason": "evidence supports HSIL",
            "disclaimer": "For reference only; does not replace clinical diagnosis.",
        }
    return {
        "tendency": "Uncertain",
        "reason": "no evidence",
        "disclaimer": "For reference only; does not replace clinical diagnosis.",
    }


def _workspace_tmp_file(name: str) -> Path:
    base_dir = Path("pytest_tmp_manual") / "step08_cli" / uuid4().hex
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir / name


def test_cli_requires_stain_text_or_stain_file(capsys) -> None:
    fake_retriever = _FakeRetriever(similar_cases=[])

    exit_code = main(
        ["--top-k", "5"],
        retriever_factory=lambda: fake_retriever,
        tendency_fn=_fake_tendency,
    )

    assert exit_code == 2
    captured = capsys.readouterr()
    assert "stain-text" in captured.err.lower()
    assert "stain-file" in captured.err.lower()


def test_cli_rejects_non_positive_top_k(capsys) -> None:
    fake_retriever = _FakeRetriever(similar_cases=[])

    exit_code = main(
        ["--stain-text", "query", "--top-k", "0"],
        retriever_factory=lambda: fake_retriever,
        tendency_fn=_fake_tendency,
    )

    assert exit_code == 2
    captured = capsys.readouterr()
    assert "top-k" in captured.err.lower()


def test_cli_rejects_more_than_five_image_paths(capsys) -> None:
    fake_retriever = _FakeRetriever(similar_cases=[])

    exit_code = main(
        [
            "--stain-text",
            "query",
            "--image-paths",
            "1.jpg",
            "2.jpg",
            "3.jpg",
            "4.jpg",
            "5.jpg",
            "6.jpg",
        ],
        retriever_factory=lambda: fake_retriever,
        tendency_fn=_fake_tendency,
    )

    assert exit_code == 2
    captured = capsys.readouterr()
    assert "image-paths" in captured.err.lower()
    assert "5" in captured.err


def test_cli_outputs_structured_json(capsys) -> None:
    similar_cases = [
        {
            "case_id": "CASE-001",
            "label": "HSIL",
            "similarity": 0.93,
            "evidence": "sample evidence",
            "metadata": {"case_id": "CASE-001", "label": "HSIL"},
        }
    ]
    fake_retriever = _FakeRetriever(similar_cases=similar_cases)

    exit_code = main(
        ["--case-id", "Q-001", "--stain-text", "query text", "--top-k", "5"],
        retriever_factory=lambda: fake_retriever,
        tendency_fn=_fake_tendency,
    )

    assert exit_code == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert set(payload.keys()) == {
        "similar_cases",
        "tendency",
        "reason",
        "disclaimer",
        "meta",
    }
    assert payload["similar_cases"] == similar_cases
    assert payload["tendency"] == "HSIL"
    assert payload["reason"] == "evidence supports HSIL"
    assert payload["meta"]["top_k"] == 5
    assert payload["meta"]["retrieval_mode"] == "vector_only"
    assert payload["meta"]["query_case_id"] == "Q-001"


def test_cli_reads_stain_file_input(capsys) -> None:
    stain_file = _workspace_tmp_file("stain.txt")
    stain_file.write_text("text from file", encoding="utf-8")
    fake_retriever = _FakeRetriever(similar_cases=[])

    exit_code = main(
        ["--stain-file", str(stain_file), "--top-k", "3"],
        retriever_factory=lambda: fake_retriever,
        tendency_fn=_fake_tendency,
    )

    assert exit_code == 0
    assert fake_retriever.calls == [("text from file", 3)]
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["meta"]["top_k"] == 3
    assert payload["meta"]["query_case_id"] is None


def test_cli_returns_error_when_stain_file_missing(capsys) -> None:
    fake_retriever = _FakeRetriever(similar_cases=[])

    exit_code = main(
        ["--stain-file", "missing-file.txt"],
        retriever_factory=lambda: fake_retriever,
        tendency_fn=_fake_tendency,
    )

    assert exit_code == 2
    captured = capsys.readouterr()
    assert "stain-file" in captured.err.lower()
    assert "missing-file.txt" in captured.err
