from __future__ import annotations

from src.reasoning.tendency_service import (
    DEFAULT_DISCLAIMER,
    infer_tendency,
)


def _similar_case(label: str, similarity: float) -> dict[str, object]:
    return {
        "case_id": f"{label}-{similarity}",
        "label": label,
        "similarity": similarity,
        "evidence": f"evidence-{label}",
        "metadata": {"label": label},
    }


def test_uncertain_when_low_top1_and_low_majority_ratio() -> None:
    similar_cases = [
        _similar_case("HSIL", 0.59),
        _similar_case("HSIL", 0.57),
        _similar_case("LSIL", 0.55),
    ]

    result = infer_tendency(similar_cases, top_k=6)

    assert result["tendency"] == "Uncertain"
    assert "top1_similarity" in result["reason"]
    assert "majority_ratio" in result["reason"]


def test_uncertain_when_labels_are_tied() -> None:
    similar_cases = [
        _similar_case("HSIL", 0.92),
        _similar_case("LSIL", 0.86),
        _similar_case("HSIL", 0.83),
        _similar_case("LSIL", 0.81),
    ]

    result = infer_tendency(similar_cases, top_k=4)

    assert result["tendency"] == "Uncertain"
    assert "tie" in result["reason"].lower()


def test_majority_hsil_when_evidence_is_sufficient() -> None:
    similar_cases = [
        _similar_case("HSIL", 0.88),
        _similar_case("HSIL", 0.84),
        _similar_case("HSIL", 0.80),
        _similar_case("LSIL", 0.76),
    ]

    result = infer_tendency(similar_cases, top_k=5)

    assert result["tendency"] == "HSIL"
    assert "HSIL" in result["reason"]


def test_majority_lsil_when_evidence_is_sufficient() -> None:
    similar_cases = [
        _similar_case("LSIL", 0.87),
        _similar_case("LSIL", 0.85),
        _similar_case("LSIL", 0.79),
        _similar_case("HSIL", 0.77),
    ]

    result = infer_tendency(similar_cases, top_k=5)

    assert result["tendency"] == "LSIL"
    assert "LSIL" in result["reason"]


def test_result_contains_required_fields() -> None:
    similar_cases = [
        _similar_case("HSIL", 0.93),
        _similar_case("HSIL", 0.89),
    ]

    result = infer_tendency(similar_cases, top_k=5)

    assert set(result.keys()) == {"tendency", "reason", "disclaimer"}
    assert result["disclaimer"] == DEFAULT_DISCLAIMER
