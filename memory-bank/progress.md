step_id: STEP-01
step_order: 1
step_title: 定义病例元数据结构与输入输出契约
status: done
automated_test: conda run -n vibe-rag python -m pytest -k case_record_schema -q -> 3 passed; conda run -n vibe-rag python -m pytest -q -> 3 passed
manual_test: 用户确认人工验证通过，覆盖缺少 case_id、缺少 report_time、非法 label 三类路径
changes: 新增 tests/test_case_record_schema.py 的缺少 report_time 校验测试；在 src/models/case_record.py 中统一必填字段错误到 CaseRecordValidationError，并抽取 _require_datetime 辅助函数
notes: STEP-01 仅在当前 step 范围内完成，未跨 step 实现；commit_ref 已回填 d451f69
commit_ref: d451f69
updated_at: 2026-02-21T15:38:00.7371671+08:00

step_id: STEP-02
step_order: 2
step_title: 实现数据目录扫描与完整性校验
status: done
automated_test: python -m pytest -k case_scanner -q -> 2 passed, 3 deselected; python -m pytest -q -> 5 passed
manual_test: 用户确认人工验证通过，覆盖合法目录发现与缺失文件报错场景
changes: 新增 tests/test_case_scanner.py；新增 src/ingestion/__init__.py 与 src/ingestion/case_scanner.py；实现 scan_case_directories 与 ScannedCase/ScanIssue 输出
notes: STEP-02 仅在当前 step 范围内完成，未跨 step 实现；未触发 architecture 更新（非里程碑/非主要功能）
commit_ref: 71b7ab0
updated_at: 2026-02-21T17:18:10.0429147+08:00

step_id: STEP-03
step_order: 3
step_title: 实现 UTF-8 与 0x7F 文本清洗
status: done
automated_test: conda run -n vibe-rag python -m pytest -k text_cleaner -q -> 3 passed, 5 deselected; conda run -n vibe-rag python -m pytest -q -> 8 passed
manual_test: 用户确认人工验证通过，覆盖控制字符清洗与 UTF-8 解码错误处理
changes: 新增 tests/test_text_cleaner.py；新增 src/ingestion/text_cleaner.py，提供 clean_text/read_and_clean_text 与 TextCleaningError
notes: STEP-03 仅在当前 step 范围内完成，未跨 step 实现；等待 commit hash 回填；未收到明确指令前不得进入 STEP-04
commit_ref: 20e4413
updated_at: 2026-02-21T21:08:31.2424643+08:00

step_id: STEP-04
step_order: 4
step_title: 从 PDF 文件名解析报告时间并写入 JSONL 元数据
status: done
automated_test: conda run -n vibe-rag python -m pytest -k metadata_store -q -> 3 passed, 8 deselected; conda run -n vibe-rag python -m pytest -q -> 11 passed
manual_test: 用户确认进入 git 阶段，按规则视为 STEP-04 验收流人工验证通过
changes: 新增 tests/test_metadata_store.py；新增 src/ingestion/report_time_parser.py 与 src/ingestion/metadata_store.py；实现 PDF 时间戳解析与 JSONL 元数据 build/write/read
notes: STEP-04 仅在当前 step 范围内完成；达到 EPIC-INGESTION 里程碑并同步 architecture；未收到明确指令前不得进入 STEP-05
commit_ref: 88c3023
updated_at: 2026-02-21T21:57:29.9519960+08:00

step_id: STEP-05
step_order: 5
step_title: 构建用于向量化输入的检索文档对象
status: done
automated_test: conda run -n vibe-rag python -m pytest -k document_builder -q -> initial expected failure (ModuleNotFoundError: src.retrieval); conda run -n vibe-rag python -m pytest -k document_builder -q --ignore pytest_tmp_manual --ignore .pytest_tmp --ignore .pytest_tmp_run_20260221 -> 6 passed; conda run -n vibe-rag python -m pytest -k "document_builder or metadata_store" -q --ignore pytest_tmp_manual --ignore .pytest_tmp --ignore .pytest_tmp_run_20260221 (outside sandbox) -> 9 passed, 8 deselected; conda run -n vibe-rag python -m pytest -q --ignore pytest_tmp_manual --ignore .pytest_tmp --ignore .pytest_tmp_run_20260221 (outside sandbox) -> 17 passed
manual_test: 用户确认人工验证通过，覆盖无 report_text、有 report_text、非法 stain_text 三个场景
changes: 新增 tests/test_document_builder.py；新增 src/retrieval/__init__.py 与 src/retrieval/document_builder.py；实现 RetrievalDocument、DocumentBuildError 及单条/批量构建函数
notes: STEP-05 仅在当前 step 范围内完成，未跨 step 实现；.gitignore 已补充 pytest_tmp_manual/；等待 commit hash 回填
commit_ref: 1c8cee7
updated_at: 2026-02-22T13:28:38.8338479+08:00

step_id: STEP-06
step_order: 6
step_title: 实现 vector-only 检索链路（API client + Chroma Top-K）
status: done
automated_test: conda run -n vibe-rag python -m pytest -k "api_client or retriever_topk" -q --ignore pytest_tmp_manual --ignore .pytest_tmp --ignore .pytest_tmp_run_20260221 -> initial expected failure (ModuleNotFoundError: src.infra, src.retrieval.retriever); conda run -n vibe-rag python -m pytest -k "api_client or retriever_topk" -q --ignore pytest_tmp_manual --ignore .pytest_tmp --ignore .pytest_tmp_run_20260221 -> 9 passed, 17 deselected; conda run -n vibe-rag python -m pytest -q --ignore pytest_tmp_manual --ignore .pytest_tmp --ignore .pytest_tmp_run_20260221 -> 26 passed; conda run -n vibe-rag python -m pytest -k "api_client or retriever_topk" -q --ignore pytest_tmp_manual --ignore .pytest_tmp --ignore .pytest_tmp_run_20260221 -> 9 passed, 17 deselected; conda run -n vibe-rag python -m pytest -k "api_client or retriever_topk" -q --ignore pytest_tmp_manual --ignore .pytest_tmp --ignore .pytest_tmp_run_20260221 -> 9 passed, 22 deselected; conda run -n vibe-rag python -m pytest -q --ignore pytest_tmp_manual --ignore .pytest_tmp --ignore .pytest_tmp_run_20260221 -> 31 passed
manual_test: 用户确认 STEP-06 完成并要求回归复核；回归通过后按门禁视为人工验证通过
changes: 新增 tests/test_api_client.py 与 tests/test_retriever_topk.py；新增 src/infra/__init__.py、src/infra/api_client.py、src/retrieval/vector_store_chroma.py、src/retrieval/retriever.py；更新 src/retrieval/__init__.py；更新 tests/test_case_scanner.py/tests/test_text_cleaner.py/tests/test_metadata_store.py 以使用工作区临时目录；清理 src/tests __pycache__
notes: blocker 经用户确认后解除；STEP-06 标记 done 以允许进入 STEP-07；阻塞期间未执行跨 step 实现
commit_ref: a5d5c0f
updated_at: 2026-02-22T14:58:03.8394165+08:00

step_id: STEP-07
step_order: 7
step_title: 实现 HSIL/LSIL/Uncertain 倾向判定与可解释理由
status: done
automated_test: conda run -n vibe-rag python -m pytest -k tendency_service -q --ignore pytest_tmp_manual --ignore .pytest_tmp --ignore .pytest_tmp_run_20260221 -> expected failure (ModuleNotFoundError: src.reasoning); conda run -n vibe-rag python -m pytest -k tendency_service -q --ignore pytest_tmp_manual --ignore .pytest_tmp --ignore .pytest_tmp_run_20260221 -> 5 passed, 26 deselected; conda run -n vibe-rag python -m pytest -k tendency_service -q --ignore pytest_tmp_manual --ignore .pytest_tmp --ignore .pytest_tmp_run_20260221 -> 5 passed, 26 deselected (post-refactor); conda run -n vibe-rag python -m pytest -q --ignore pytest_tmp_manual --ignore .pytest_tmp --ignore .pytest_tmp_run_20260221 -> 31 passed; conda run -n vibe-rag python -m pytest -k tendency_service -q --ignore pytest_tmp_manual --ignore .pytest_tmp --ignore .pytest_tmp_run_20260221 -> 5 passed, 26 deselected (post-optimization); conda run -n vibe-rag python -m pytest -q --ignore pytest_tmp_manual --ignore .pytest_tmp --ignore .pytest_tmp_run_20260221 -> 31 passed; conda run -n vibe-rag python -m pytest -k api_client -q --ignore pytest_tmp_manual --ignore .pytest_tmp --ignore .pytest_tmp_run_20260221 -> expected failure after test-first dual-provider update (3 failed, 8 passed), then expected failure after minimal implementation (2 failed, 9 passed), then green after deterministic env test fix (11 passed, 24 deselected); conda run -n vibe-rag python -m pytest -q --ignore pytest_tmp_manual --ignore .pytest_tmp --ignore .pytest_tmp_run_20260221 -> 35 passed
manual_test: 用户确认 STEP-07 完成并已提交 commit；双 provider 真实 API smoke（embed_texts + generate_reasoning）通过
changes: 新增 tests/test_tendency_service.py；新增 src/reasoning/__init__.py 与 src/reasoning/tendency_service.py；实现 infer_tendency（含阈值、并列返回 Uncertain、固定输出字段、通用常量与辅助函数、不支持标签兜底）；更新 tests/test_api_client.py 以匹配双 provider 契约；重构 src/infra/api_client.py 拆分 embedding/generation 配置与路由
notes: 在 STEP-07 范围内完成 TDD red->green->refactor；按用户要求合入双 provider 重构；步骤关闭并完成 commit 回填；未收到明确指令前不得进入 STEP-08
commit_ref: 3d46362
updated_at: 2026-02-22T15:25:49.8180285+08:00

step_id: STEP-08
step_order: 8
step_title: 提供本地 CLI 入口并输出结构化 JSON
status: done
automated_test: conda run -n vibe-rag python -m pytest -k cli_main -q --ignore pytest_tmp_manual --ignore .pytest_tmp --ignore .pytest_tmp_run_20260221 -> expected failure (ModuleNotFoundError: src.cli); conda run -n vibe-rag python -m pytest -k cli_main -q --ignore pytest_tmp_manual --ignore .pytest_tmp --ignore .pytest_tmp_run_20260221 -> 6 passed, 35 deselected; conda run -n vibe-rag python -m pytest -q --ignore pytest_tmp_manual --ignore .pytest_tmp --ignore .pytest_tmp_run_20260221 -> 41 passed
manual_test: 待用户确认 CLI 成功路径与参数错误路径
changes: 新增 tests/test_cli_main.py；新增 src/cli/__init__.py 与 src/cli/main.py；实现 CLI 参数校验（必须提供 stain 输入、top_k>0、image_paths 最多 5 条）、stain-file UTF-8 加载、retrieval+tendency 编排、结构化 JSON 输出与稳定退出码（argument=2、runtime=1）
notes: STEP-08 在当前 step 范围内完成严格 TDD red->green->refactor；记录中仍保留“待人工确认”历史语义；commit_ref 已由用户提供并回填 [main 58de3fc]
commit_ref: 58de3fc
updated_at: 2026-02-22T15:41:43.0707509+08:00

step_id: STEP-09
step_order: 9
step_title: 完成 V1 回归与失败路径覆盖基线
status: done
automated_test: conda run -n vibe-rag python -m pytest -k "e2e_v1_baseline or failure_paths" -q --ignore pytest_tmp_manual --ignore .pytest_tmp --ignore .pytest_tmp_run_20260221 -> expected failure (1 failed, 9 passed; invalid UTF-8 stain-file returned runtime code 1 instead of argument code 2); conda run -n vibe-rag python -m pytest -k "e2e_v1_baseline or failure_paths" -q --ignore pytest_tmp_manual --ignore .pytest_tmp --ignore .pytest_tmp_run_20260221 -> 10 passed, 41 deselected; conda run -n vibe-rag python -m pytest -q --ignore pytest_tmp_manual --ignore .pytest_tmp --ignore .pytest_tmp_run_20260221 -> 51 passed
manual_test: 用户确认状态收口，并基于 docs/manual-acceptance-v1.md（M1-M4）接受 STEP-09 完成
changes: 新增 tests/test_e2e_v1_baseline.py 与 tests/test_failure_paths.py；更新 src/cli/main.py 将 stain-file UTF-8 解码失败映射为 CliArgumentError；新增 docs/manual-acceptance-v1.md
notes: STEP-09 在当前 step 范围内标记为 done；达到 EPIC-QA 里程碑；未发生跨 step 实现，且未执行 git 操作
commit_ref: bb61c10
updated_at: 2026-02-22T16:06:07.3608517+08:00

step_id: STEP-10
step_order: 10
step_title: 中文友好与新手友好重构文档同步
status: done
automated_test: not run (docs-only step)
manual_test: 已完成 progress/implementation-plan/prd/tech-stack/architecture 与 AGENTS/manual-acceptance 的文档一致性复核；术语、范围、兼容约束与非目标保持一致
changes: 完成 STEP-10 docs-only 收口；同步更新 memory-bank/progress.md、docs/manual-acceptance-v1.md、AGENTS.md 的中文友好文案，并保持关键 token/键名兼容
notes: STEP-10 在当前 step 范围内收口完成；记录 EPIC-UX-LOCALIZATION 文档里程碑；未修改 src/ 或 tests/ 行为实现；未收到明确指令前不得进入 STEP-11
commit_ref: pending
updated_at: 2026-02-22T16:30:32.9111855+08:00
