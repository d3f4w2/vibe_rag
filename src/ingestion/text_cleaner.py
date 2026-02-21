from __future__ import annotations

from pathlib import Path

_CONTROL_CHARS_TO_REMOVE: tuple[str, ...] = ("\x7f",)


class TextCleaningError(ValueError):
    """Raised when text cleaning input or file reading is invalid."""


def clean_text(text: str) -> str:
    if not isinstance(text, str):
        raise TextCleaningError("text must be a string.")

    cleaned = text
    for control_char in _CONTROL_CHARS_TO_REMOVE:
        cleaned = cleaned.replace(control_char, "")

    return cleaned


def read_and_clean_text(path: str | Path) -> str:
    text_path = Path(path)
    try:
        raw_text = text_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise TextCleaningError(
            f"failed to decode {text_path.name} as UTF-8 text."
        ) from exc
    except OSError as exc:
        raise TextCleaningError(f"failed to read text file: {text_path}") from exc

    return clean_text(raw_text)
