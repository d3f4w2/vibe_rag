step_id: STEP-01
step_order: 1
step_title: 定义病例元数据结构与输入输出契约
status: done
automated_test: conda run -n vibe-rag python -m pytest -k case_record_schema -q -> 3 passed; conda run -n vibe-rag python -m pytest -q -> 3 passed
manual_test: user confirmed manual verification passed for missing case_id, missing report_time, and invalid label error paths
changes: tests/test_case_record_schema.py added missing report_time validation test; src/models/case_record.py normalized required-field errors to CaseRecordValidationError and extracted _require_datetime helper
notes: STEP-01 completed under current-step scope only; no cross-step implementation; commit_ref to be backfilled after commit
commit_ref: d451f69
updated_at: 2026-02-21T15:37:25.9313955+08:00
