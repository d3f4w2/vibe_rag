step_id: STEP-01
step_order: 1
step_title: 定义病例元数据结构与输入输出契约
status: done
automated_test: conda run -n vibe-rag python -m pytest -k case_record_schema -q -> 3 passed; conda run -n vibe-rag python -m pytest -q -> 3 passed
manual_test: user confirmed manual verification passed for missing case_id, missing report_time, and invalid label error paths
changes: tests/test_case_record_schema.py added missing report_time validation test; src/models/case_record.py normalized required-field errors to CaseRecordValidationError and extracted _require_datetime helper
notes: STEP-01 completed under current-step scope only; no cross-step implementation; commit_ref backfilled to d451f69
commit_ref: d451f69
updated_at: 2026-02-21T15:38:00.7371671+08:00

step_id: STEP-02
step_order: 2
step_title: Implement data directory scanning and integrity checks
status: done
automated_test: python -m pytest -k case_scanner -q -> 2 passed, 3 deselected; python -m pytest -q -> 5 passed
manual_test: user confirmed manual verification passed for valid directory discovery and missing-file error reporting
changes: added tests/test_case_scanner.py; added src/ingestion/__init__.py and src/ingestion/case_scanner.py; implemented scan_case_directories with ScannedCase/ScanIssue outputs
notes: STEP-02 completed under current-step scope only; no cross-step implementation; architecture update not triggered (not milestone/major feature)
commit_ref: 71b7ab0
updated_at: 2026-02-21T17:18:10.0429147+08:00
