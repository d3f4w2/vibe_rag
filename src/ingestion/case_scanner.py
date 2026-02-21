from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.models.case_record import AllowedLabel

_SUPPORTED_LABELS: tuple[AllowedLabel, ...] = ("HSIL", "LSIL")
_REQUIRED_IMAGE_FILES = tuple(f"{i}.jpg" for i in range(1, 6))
_REQUIRED_STAIN_FILE = "\u7740\u8272\u60c5\u51b5.txt"
_REQUIRED_PDF_MARKER = "*.pdf"


@dataclass(frozen=True)
class ScannedCase:
    case_id: str
    label: AllowedLabel
    case_dir: str
    image_paths: list[str]
    report_pdf_path: str
    stain_text_path: str


@dataclass(frozen=True)
class ScanIssue:
    case_id: str
    label: AllowedLabel
    case_dir: str
    missing_items: list[str]


def scan_case_directories(data_root: str | Path) -> tuple[list[ScannedCase], list[ScanIssue]]:
    root = Path(data_root)
    scanned_cases: list[ScannedCase] = []
    scan_issues: list[ScanIssue] = []

    for case_dir, label in _iter_case_dirs(root):
        missing_items, image_paths, report_pdf_path, stain_text_path = _inspect_case_dir(
            case_dir=case_dir
        )
        if missing_items:
            scan_issues.append(
                ScanIssue(
                    case_id=case_dir.name,
                    label=label,
                    case_dir=str(case_dir),
                    missing_items=missing_items,
                )
            )
            continue

        scanned_cases.append(
            ScannedCase(
                case_id=case_dir.name,
                label=label,
                case_dir=str(case_dir),
                image_paths=image_paths,
                report_pdf_path=report_pdf_path,
                stain_text_path=stain_text_path,
            )
        )

    return scanned_cases, scan_issues


def _iter_case_dirs(data_root: Path) -> list[tuple[Path, AllowedLabel]]:
    case_dirs: list[tuple[Path, AllowedLabel]] = []
    for label in _SUPPORTED_LABELS:
        label_root = data_root / label
        if not label_root.exists():
            continue

        for case_dir in sorted(label_root.iterdir()):
            if case_dir.is_dir():
                case_dirs.append((case_dir, label))

    return case_dirs


def _inspect_case_dir(case_dir: Path) -> tuple[list[str], list[str], str, str]:
    missing_items: list[str] = []

    image_paths: list[str] = []
    for image_file in _REQUIRED_IMAGE_FILES:
        image_path = case_dir / image_file
        if image_path.exists():
            image_paths.append(str(image_path))
        else:
            missing_items.append(image_file)

    pdf_paths = sorted(case_dir.glob("*.pdf"))
    if len(pdf_paths) != 1:
        missing_items.append(_REQUIRED_PDF_MARKER)

    stain_text_path = case_dir / _REQUIRED_STAIN_FILE
    if not stain_text_path.exists():
        missing_items.append(_REQUIRED_STAIN_FILE)

    report_pdf_path = str(pdf_paths[0]) if len(pdf_paths) == 1 else ""
    return missing_items, image_paths, report_pdf_path, str(stain_text_path)
