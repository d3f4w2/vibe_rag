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

step_id: STEP-05
step_order: 5
step_title: Build retrieval document object for vectorization input
status: done
automated_test: conda run -n vibe-rag python -m pytest -k document_builder -q -> initial expected failure (ModuleNotFoundError: src.retrieval); conda run -n vibe-rag python -m pytest -k document_builder -q --ignore pytest_tmp_manual --ignore .pytest_tmp --ignore .pytest_tmp_run_20260221 -> 6 passed; conda run -n vibe-rag python -m pytest -k "document_builder or metadata_store" -q --ignore pytest_tmp_manual --ignore .pytest_tmp --ignore .pytest_tmp_run_20260221 (outside sandbox) -> 9 passed, 8 deselected; conda run -n vibe-rag python -m pytest -q --ignore pytest_tmp_manual --ignore .pytest_tmp --ignore .pytest_tmp_run_20260221 (outside sandbox) -> 17 passed
manual_test: user confirmed manual verification passed for retrieval document build scenarios (without report_text, with report_text, and invalid stain_text error path)
changes: added tests/test_document_builder.py; added src/retrieval/__init__.py and src/retrieval/document_builder.py; implemented RetrievalDocument, DocumentBuildError, and builders for single/batch metadata records
notes: STEP-05 completed under current-step scope only; no cross-step implementation; .gitignore updated to include pytest_tmp_manual/ for clean git stage; waiting for commit hash backfill
commit_ref: 1c8cee7
updated_at: 2026-02-22T13:28:38.8338479+08:00

step_id: STEP-06
step_order: 6
step_title: Implement vector-only retrieval pipeline with API client and Chroma Top-K
status: blocked
automated_test: conda run -n vibe-rag python -m pytest -k "api_client or retriever_topk" -q --ignore pytest_tmp_manual --ignore .pytest_tmp --ignore .pytest_tmp_run_20260221 -> initial expected failure (ModuleNotFoundError: src.infra, src.retrieval.retriever); conda run -n vibe-rag python -m pytest -k "api_client or retriever_topk" -q --ignore pytest_tmp_manual --ignore .pytest_tmp --ignore .pytest_tmp_run_20260221 -> 9 passed, 17 deselected; conda run -n vibe-rag python -m pytest -q --ignore pytest_tmp_manual --ignore .pytest_tmp --ignore .pytest_tmp_run_20260221 -> 26 passed; conda run -n vibe-rag python -m pytest -k "api_client or retriever_topk" -q --ignore pytest_tmp_manual --ignore .pytest_tmp --ignore .pytest_tmp_run_20260221 -> 9 passed, 17 deselected
manual_test: pending human verification for valid API retrieval, invalid API key auth error, and top_k behavior checks
changes: added tests/test_api_client.py and tests/test_retriever_topk.py; added src/infra/__init__.py and src/infra/api_client.py; added src/retrieval/vector_store_chroma.py and src/retrieval/retriever.py; updated src/retrieval/__init__.py; updated tests/test_case_scanner.py tests/test_text_cleaner.py tests/test_metadata_store.py to use workspace temp dirs for stable pytest execution; removed src/tests __pycache__ directories during cleanup pass
notes: blocker removed and resumed by confirmed env setup (httpx/chromadb available; EMBEDDING_API_BASE_URL/KEY/MODEL provided); implemented vector_only retrieval path and unified API error mapping within STEP-06 scope only; cleanup request partially blocked by filesystem ACL/permission denial when deleting .pytest_tmp .pytest_tmp_step06 .pytest_tmp_run_20260221 pytest_tmp_manual .pytest_cache (and locked subdirs); unblock conditions = run cleanup with OS-level admin permission or manually take ownership/reset ACL for locked directories, then rerun deletion and verification
commit_ref: pending
updated_at: 2026-02-22T14:46:39.5849949+08:00
