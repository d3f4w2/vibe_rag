from pathlib import Path
from uuid import uuid4

import pytest

from src.ingestion.text_cleaner import TextCleaningError, clean_text, read_and_clean_text


def _workspace_tmp_dir() -> Path:
    root = Path("pytest_tmp_manual") / "step06_text_cleaner" / uuid4().hex
    root.mkdir(parents=True, exist_ok=True)
    return root


def test_clean_text_removes_del_control_char_and_preserves_order() -> None:
    raw_text = "line1\x7f line2\x7f line3"

    cleaned = clean_text(raw_text)

    assert cleaned == "line1 line2 line3"
    assert "\x7f" not in cleaned


def test_read_and_clean_text_reads_utf8_and_cleans_del_char() -> None:
    text_path = _workspace_tmp_dir() / "\u7740\u8272\u60c5\u51b5.txt"
    text_path.write_text("abc\x7fdef", encoding="utf-8")

    cleaned = read_and_clean_text(text_path)

    assert cleaned == "abcdef"
    assert "\x7f" not in cleaned


def test_read_and_clean_text_raises_error_on_utf8_decode_failure() -> None:
    text_path = _workspace_tmp_dir() / "bad-encoding.txt"
    text_path.write_bytes(b"\xff\xfe\xfa")

    with pytest.raises(TextCleaningError) as exc_info:
        read_and_clean_text(text_path)

    error_text = str(exc_info.value)
    assert "utf-8" in error_text.lower()
    assert text_path.name in error_text
