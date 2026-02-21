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

step_id: STEP-03
step_order: 3
step_title: Implement text cleaning for UTF-8 and 0x7F removal
status: done
automated_test: conda run -n vibe-rag python -m pytest -k text_cleaner -q -> 3 passed, 5 deselected; conda run -n vibe-rag python -m pytest -q -> 8 passed
manual_test: user confirmed manual verification passed for control-char cleanup and UTF-8 decode error handling
changes: added tests/test_text_cleaner.py; added src/ingestion/text_cleaner.py with clean_text/read_and_clean_text and TextCleaningError
notes: STEP-03 completed under current-step scope only; no cross-step implementation; waiting for commit hash backfill; do not enter STEP-04 without explicit start next step
commit_ref: 20e4413
updated_at: 2026-02-21T21:08:31.2424643+08:00

step_id: STEP-04
step_order: 4
step_title: Parse report timestamp from PDF filename and persist JSONL metadata
status: done
automated_test: conda run -n vibe-rag python -m pytest -k metadata_store -q -> 3 passed, 8 deselected; conda run -n vibe-rag python -m pytest -q -> 11 passed
manual_test: user confirmed moving to git stage, treated as manual verification passed for STEP-04 acceptance flow
changes: added tests/test_metadata_store.py; added src/ingestion/report_time_parser.py and src/ingestion/metadata_store.py; implemented PDF timestamp parsing and JSONL metadata build/write/read
notes: STEP-04 completed under current-step scope only; milestone EPIC-INGESTION reached; architecture synced; do not enter STEP-05 without explicit start next step
commit_ref: 88c3023
updated_at: 2026-02-21T21:57:29.9519960+08:00
