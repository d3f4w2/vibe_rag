from pathlib import Path

from src.ingestion.case_scanner import scan_case_directories


def _create_complete_case(data_root: Path, label: str, case_id: str) -> Path:
    case_dir = data_root / label / case_id
    case_dir.mkdir(parents=True, exist_ok=True)

    for i in range(1, 6):
        (case_dir / f"{i}.jpg").write_bytes(b"jpg")

    (case_dir / f"{case_id}_\u68c0\u67e5\u62a5\u544a_20240212091530.pdf").write_bytes(
        b"%PDF-1.4"
    )
    (case_dir / "\u7740\u8272\u60c5\u51b5.txt").write_text("sample stain text", encoding="utf-8")
    return case_dir


def test_scan_case_directories_discovers_valid_cases_with_labels(tmp_path: Path) -> None:
    _create_complete_case(tmp_path, "HSIL", "CASE-H-001")
    _create_complete_case(tmp_path, "LSIL", "CASE-L-001")

    cases, errors = scan_case_directories(tmp_path)

    assert errors == []
    assert {(case.case_id, case.label) for case in cases} == {
        ("CASE-H-001", "HSIL"),
        ("CASE-L-001", "LSIL"),
    }

    case_h = next(case for case in cases if case.case_id == "CASE-H-001")
    assert [Path(path).name for path in case_h.image_paths] == [
        "1.jpg",
        "2.jpg",
        "3.jpg",
        "4.jpg",
        "5.jpg",
    ]
    assert Path(case_h.stain_text_path).name == "\u7740\u8272\u60c5\u51b5.txt"
    assert Path(case_h.report_pdf_path).suffix == ".pdf"


def test_scan_case_directories_reports_missing_required_files(tmp_path: Path) -> None:
    bad_case_dir = tmp_path / "HSIL" / "CASE-BAD-001"
    bad_case_dir.mkdir(parents=True, exist_ok=True)
    for file_name in ("1.jpg", "2.jpg", "4.jpg", "5.jpg"):
        (bad_case_dir / file_name).write_bytes(b"jpg")

    cases, errors = scan_case_directories(tmp_path)

    assert cases == []
    assert len(errors) == 1

    issue = errors[0]
    assert issue.case_id == "CASE-BAD-001"
    assert issue.label == "HSIL"
    assert Path(issue.case_dir).name == "CASE-BAD-001"
    assert set(issue.missing_items) == {"3.jpg", "*.pdf", "\u7740\u8272\u60c5\u51b5.txt"}
