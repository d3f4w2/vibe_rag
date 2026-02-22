from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Callable, Protocol

from src.reasoning.tendency_service import infer_tendency
from src.retrieval.retriever import build_default_vector_only_retriever

RETRIEVAL_MODE = "vector_only"


class CliArgumentError(ValueError):
    """Raised when CLI arguments are invalid."""


class RetrieverProtocol(Protocol):
    def retrieve(self, query_text: str, *, top_k: int) -> list[dict[str, object]]:
        ...


class TendencyFnProtocol(Protocol):
    def __call__(
        self,
        similar_cases: list[dict[str, object]],
        *,
        top_k: int,
    ) -> dict[str, str]:
        ...


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise CliArgumentError(message)


def _positive_int(raw_value: str) -> int:
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("top-k must be an integer.") from exc
    if value <= 0:
        raise argparse.ArgumentTypeError("top-k must be greater than 0.")
    return value


def _build_parser() -> argparse.ArgumentParser:
    parser = _Parser(prog="rag-query")
    parser.add_argument("--case-id", default=None)
    parser.add_argument("--stain-text", default=None)
    parser.add_argument("--stain-file", default=None)
    parser.add_argument("--report-text", default=None)
    parser.add_argument("--image-paths", nargs="*", default=[])
    parser.add_argument("--top-k", type=_positive_int, default=5)
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = _build_parser()
    args = parser.parse_args(argv)
    _validate_args(args)
    return args


def _validate_args(args: argparse.Namespace) -> None:
    has_stain_text = isinstance(args.stain_text, str) and bool(args.stain_text.strip())
    has_stain_file = isinstance(args.stain_file, str) and bool(args.stain_file.strip())

    if not has_stain_text and not has_stain_file:
        raise CliArgumentError("either --stain-text or --stain-file must be provided.")

    if len(args.image_paths) > 5:
        raise CliArgumentError("--image-paths allows at most 5 entries.")


def _resolve_stain_text(args: argparse.Namespace) -> str:
    if isinstance(args.stain_text, str) and args.stain_text.strip():
        return args.stain_text.strip()

    if not isinstance(args.stain_file, str) or not args.stain_file.strip():
        raise CliArgumentError("either --stain-text or --stain-file must be provided.")

    stain_file_path = Path(args.stain_file)
    try:
        content = stain_file_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise CliArgumentError(
            f"failed to read --stain-file '{args.stain_file}': {exc}"
        ) from exc

    if not content.strip():
        raise CliArgumentError("--stain-file must contain non-empty UTF-8 text.")

    return content


def _build_result_payload(
    *,
    similar_cases: list[dict[str, object]],
    tendency_payload: dict[str, str],
    top_k: int,
    case_id: str | None,
) -> dict[str, object]:
    return {
        "similar_cases": similar_cases,
        "tendency": tendency_payload["tendency"],
        "reason": tendency_payload["reason"],
        "disclaimer": tendency_payload["disclaimer"],
        "meta": {
            "top_k": top_k,
            "retrieval_mode": RETRIEVAL_MODE,
            "query_case_id": case_id,
        },
    }


def run_query(
    args: argparse.Namespace,
    *,
    retriever_factory: Callable[[], RetrieverProtocol],
    tendency_fn: TendencyFnProtocol,
) -> dict[str, object]:
    stain_text = _resolve_stain_text(args)
    retriever = retriever_factory()
    similar_cases = retriever.retrieve(stain_text, top_k=args.top_k)

    tendency_payload = tendency_fn(similar_cases, top_k=args.top_k)
    return _build_result_payload(
        similar_cases=similar_cases,
        tendency_payload=tendency_payload,
        top_k=args.top_k,
        case_id=args.case_id,
    )


def main(
    argv: list[str] | None = None,
    *,
    retriever_factory: Callable[[], RetrieverProtocol] = build_default_vector_only_retriever,
    tendency_fn: TendencyFnProtocol = infer_tendency,
) -> int:
    try:
        args = parse_args(argv)
        payload = run_query(args, retriever_factory=retriever_factory, tendency_fn=tendency_fn)
    except CliArgumentError as exc:
        print(f"argument error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"runtime error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
