from __future__ import annotations

from collections import Counter

DEFAULT_DISCLAIMER = "For reference only; does not replace clinical diagnosis."

_HSIL = "HSIL"
_LSIL = "LSIL"
_SUPPORTED_LABELS = {_HSIL, _LSIL}

UNCERTAIN_TOP1_THRESHOLD = 0.60
UNCERTAIN_MAJORITY_THRESHOLD = 0.60


def infer_tendency(
    similar_cases: list[dict[str, object]],
    *,
    top_k: int,
) -> dict[str, str]:
    if not isinstance(top_k, int) or top_k <= 0:
        raise ValueError("top_k must be a positive integer.")

    if not isinstance(similar_cases, list) or len(similar_cases) == 0:
        return {
            "tendency": "Uncertain",
            "reason": "No similar cases were retrieved, so tendency remains uncertain.",
            "disclaimer": DEFAULT_DISCLAIMER,
        }

    label_counts = _count_supported_labels(similar_cases)
    hsil_count = label_counts.get(_HSIL, 0)
    lsil_count = label_counts.get(_LSIL, 0)

    if (hsil_count + lsil_count) == 0:
        return {
            "tendency": "Uncertain",
            "reason": "Retrieved evidence does not contain supported HSIL/LSIL labels.",
            "disclaimer": DEFAULT_DISCLAIMER,
        }

    top1_similarity = _to_float(similar_cases[0].get("similarity"), default=0.0)
    majority_ratio = _compute_majority_ratio(hsil_count=hsil_count, lsil_count=lsil_count, top_k=top_k)

    if _is_label_tie(hsil_count=hsil_count, lsil_count=lsil_count):
        return {
            "tendency": "Uncertain",
            "reason": (
                "Top-K labels are tied, so tendency remains uncertain "
                f"(HSIL={hsil_count}, LSIL={lsil_count})."
            ),
            "disclaimer": DEFAULT_DISCLAIMER,
        }

    if _is_low_evidence(top1_similarity=top1_similarity, majority_ratio=majority_ratio):
        return {
            "tendency": "Uncertain",
            "reason": (
                "Evidence is weak and dispersed: "
                f"top1_similarity={top1_similarity:.2f}, "
                f"majority_ratio={majority_ratio:.2f}."
            ),
            "disclaimer": DEFAULT_DISCLAIMER,
        }

    tendency = _HSIL if hsil_count > lsil_count else _LSIL
    return {
        "tendency": tendency,
        "reason": (
            f"{tendency} is the majority label in Top-K "
            f"(HSIL={hsil_count}, LSIL={lsil_count}, top1_similarity={top1_similarity:.2f})."
        ),
        "disclaimer": DEFAULT_DISCLAIMER,
    }


def _count_supported_labels(similar_cases: list[dict[str, object]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for similar_case in similar_cases:
        label = similar_case.get("label")
        if isinstance(label, str) and label in _SUPPORTED_LABELS:
            counts[label] += 1
    return counts


def _compute_majority_ratio(*, hsil_count: int, lsil_count: int, top_k: int) -> float:
    return max(hsil_count, lsil_count) / top_k


def _is_label_tie(*, hsil_count: int, lsil_count: int) -> bool:
    return hsil_count == lsil_count and (hsil_count + lsil_count) > 0


def _is_low_evidence(*, top1_similarity: float, majority_ratio: float) -> bool:
    return (
        top1_similarity < UNCERTAIN_TOP1_THRESHOLD
        and majority_ratio < UNCERTAIN_MAJORITY_THRESHOLD
    )


def _to_float(value: object, *, default: float) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    return default
