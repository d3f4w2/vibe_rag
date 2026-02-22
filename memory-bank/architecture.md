# Architecture Baseline（Plan-Level, V1）

模块名称: ingestion.case_scanner
文件路径: src/ingestion/case_scanner.py
职责: 扫描 `data/HSIL/*` 与 `data/LSIL/*`，校验病例目录完整性（5 JPG + 1 PDF + 1 TXT）。
输入/输出: 输入为 data 根目录路径；输出为结构化病例清单与可追踪错误列表。
依赖: src/models/case_record.py
变更原因: 对齐 STEP-02，先定义数据入口边界，避免后续扫描逻辑漂移。
变更记录: 2026-02-21 workflow-init 初始化计划级模块基线。
updated_at: 2026-02-21T08:33:14.6700698+08:00

模块名称: ingestion.text_cleaner
文件路径: src/ingestion/text_cleaner.py
职责: 统一 UTF-8 读取并清理 `0x7F` 控制字符。
输入/输出: 输入为原始文本或文本文件；输出为清洗后的标准化文本。
依赖: Python 标准库编码/字符串处理。
变更原因: 对齐 STEP-03 与 PRD 验收标准 4。
变更记录: 2026-02-21 workflow-init 初始化计划级模块基线。
updated_at: 2026-02-21T08:33:14.6700698+08:00

模块名称: ingestion.report_time_parser
文件路径: src/ingestion/report_time_parser.py
职责: 从 PDF 文件名解析 `YYYYMMDDHHMMSS` 报告时间。
输入/输出: 输入为 PDF 文件名；输出为结构化时间对象或解析错误。
依赖: Python datetime、正则处理。
变更原因: 对齐 STEP-04，固定报告时间来源规则。
变更记录: 2026-02-21 workflow-init 初始化计划级模块基线。
updated_at: 2026-02-21T08:33:14.6700698+08:00

模块名称: ingestion.metadata_store
文件路径: src/ingestion/metadata_store.py
职责: 将解析后的病例元数据写入 JSONL，供检索索引使用。
输入/输出: 输入为结构化病例记录；输出为 JSONL 文件与写入状态。
依赖: src/ingestion/report_time_parser.py
变更原因: 对齐 STEP-04，形成 ingestion 到 retrieval 的稳定数据接口。
变更记录: 2026-02-21 workflow-init 初始化计划级模块基线。
updated_at: 2026-02-21T08:33:14.6700698+08:00

模块名称: retrieval.document_builder
文件路径: src/retrieval/document_builder.py
职责: 组装向量检索文档，合并 `stain_text`（必需）与 `report_text`（可选）及元数据。
输入/输出: 输入为病例结构与文本字段；输出为检索文档对象列表。
依赖: src/ingestion/metadata_store.py
变更原因: 对齐 STEP-05，固定检索输入契约。
变更记录: 2026-02-21 workflow-init 初始化计划级模块基线。
updated_at: 2026-02-21T08:33:14.6700698+08:00

模块名称: infra.api_client
文件路径: src/infra/api_client.py
职责: 统一封装 embedding/generation API 调用、超时重试与错误映射。
输入/输出: 输入为文本或 prompt；输出为向量结果或生成文本；失败时抛出统一错误类型。
依赖: httpx、pydantic-settings
变更原因: 对齐 STEP-06 决策锁定，避免业务层直接访问 HTTP。
变更记录: 2026-02-21 workflow-init 初始化计划级模块基线。
updated_at: 2026-02-21T08:33:14.6700698+08:00

模块名称: retrieval.vector_store_chroma
文件路径: src/retrieval/vector_store_chroma.py
职责: 管理 Chroma 持久化索引与向量检索操作（vector_only）。
输入/输出: 输入为文档向量与查询向量；输出为 Top-K 检索结果（含相似度）。
依赖: chroma, src/infra/api_client.py
变更原因: 对齐 STEP-06，确保检索主链路可落地。
变更记录: 2026-02-21 workflow-init 初始化计划级模块基线。
updated_at: 2026-02-21T08:33:14.6700698+08:00

模块名称: retrieval.retriever
文件路径: src/retrieval/retriever.py
职责: 编排检索流程（文档准备 -> 向量化 -> Top-K 召回 -> 证据整理）。
输入/输出: 输入为查询文本与 top_k；输出为 `similar_cases[]` 候选列表。
依赖: src/retrieval/document_builder.py, src/retrieval/vector_store_chroma.py
变更原因: 对齐 STEP-06，与后续倾向判断模块解耦。
变更记录: 2026-02-21 workflow-init 初始化计划级模块基线。
updated_at: 2026-02-21T08:33:14.6700698+08:00

模块名称: reasoning.tendency_service
文件路径: src/reasoning/tendency_service.py
职责: 基于召回证据输出 `HSIL | LSIL | Uncertain`、reason、disclaimer。
输入/输出: 输入为 Top-K 检索结果；输出为 tendency 决策对象。
依赖: src/retrieval/retriever.py
变更原因: 对齐 STEP-07，固化阈值与分散判定规则。
变更记录: 2026-02-21 workflow-init 初始化计划级模块基线。
updated_at: 2026-02-21T08:33:14.6700698+08:00

模块名称: cli.main
文件路径: src/cli/main.py
职责: 提供 `rag-query` 命令入口，执行参数校验并输出结构化 JSON。
输入/输出: 输入为 CLI 参数（case/text/top_k 等）；输出为固定字段 JSON。
依赖: src/retrieval/retriever.py, src/reasoning/tendency_service.py
变更原因: 对齐 STEP-08，固定对外交互契约。
变更记录: 2026-02-21 workflow-init 初始化计划级模块基线。
updated_at: 2026-02-21T08:33:14.6700698+08:00

模块名称: qa.acceptance_mapping
文件路径: tests/test_e2e_v1_baseline.py, tests/test_failure_paths.py
职责: 建立 PRD 验收标准与自动化测试映射（ACC-01 ~ ACC-05）。
输入/输出: 输入为系统行为与边界条件；输出为验收通过/失败结果。
依赖: 全链路模块（ingestion/retrieval/reasoning/cli/infra）
变更原因: 对齐 STEP-09，保证可验证与可追溯。
变更记录: 2026-02-21 workflow-init 初始化计划级模块基线。
updated_at: 2026-02-21T08:33:14.6700698+08:00

模块名称: ingestion.report_time_parser
文件路径: src/ingestion/report_time_parser.py
职责: 从 PDF 文件名中提取并解析 `YYYYMMDDHHMMSS` 报告时间，输出标准 datetime。
输入/输出: 输入为 PDF 文件名或路径；输出为 datetime；失败时抛出 ReportTimeParseError。
依赖: Python datetime、re、pathlib
变更原因: STEP-04 完成实现，固化报告时间来源并给元数据层提供稳定时间字段。
变更记录: 2026-02-21 完成 parse_report_time_from_pdf_filename 与错误分类。
updated_at: 2026-02-21T21:51:48.9186028+08:00

模块名称: ingestion.metadata_store
文件路径: src/ingestion/metadata_store.py
职责: 构建 CaseRecord 元数据、写入 JSONL 并支持回读校验。
输入/输出: 输入为 ScannedCase 与文本字段；输出为标准化 metadata record、写入计数、回读结果列表。
依赖: src/ingestion/report_time_parser.py、src/models/case_record.py、json、pathlib
变更原因: STEP-04 完成实现，建立 ingestion 到后续 retrieval 的稳定元数据接口。
变更记录: 2026-02-21 实现 build_metadata_record/write_metadata_jsonl/read_metadata_jsonl 并通过测试。
updated_at: 2026-02-21T21:51:48.9186028+08:00

模块名称: milestone.epic_ingestion
文件路径: memory-bank/progress.md, memory-bank/implementation-plan.md
职责: 标记 EPIC-INGESTION（STEP-01~STEP-04）完成，作为后续检索阶段起点。
输入/输出: 输入为 step 完成状态；输出为里程碑达成记录与架构文档同步说明。
依赖: STEP-01, STEP-02, STEP-03, STEP-04
变更原因: 满足里程碑触发条件，需要同步 architecture 文档。
变更记录: 2026-02-21 EPIC-INGESTION 达成并完成 architecture 同步。
updated_at: 2026-02-21T21:51:48.9186028+08:00

module_name: infra.api_client (implemented)
file_path: src/infra/api_client.py
responsibility: unify embedding/generation HTTP calls, load env/.env, split provider endpoints for embedding and generation, and map timeout/auth/rate-limit/server errors to typed exceptions.
input_output: input=text list/prompt with provider-specific env config; output=embedding vectors/generated text; errors=ApiTimeoutError/ApiAuthError/ApiRateLimitError/ApiResponseError.
dependencies: httpx, os/pathlib; shared by retrieval layer.
change_reason: STEP-06 required API adapter boundary; 2026-02-22 requirement-change refactor split embedding/generation endpoints to support mixed-vendor model routing.
change_record: 2026-02-22 implemented embed_texts/generate_reasoning and provider URL normalization for stable real API path; 2026-02-22 refactored to dual-provider config (EMBEDDING_* and GENERATION_*) with independent base_url/api_key/timeout/retries.
updated_at: 2026-02-22T15:19:19.9193124+08:00

module_name: retrieval.vector_store_chroma (implemented)
file_path: src/retrieval/vector_store_chroma.py
responsibility: manage Chroma persistent collection, upsert embedded retrieval documents, and query Top-K with similarity + source metadata.
input_output: input=RetrievalDocument list + vectors/query vector; output=similar case records with case_id/label/similarity/evidence/metadata.
dependencies: chromadb, src/retrieval/document_builder.py, src/infra/api_client.load_dotenv_if_present.
change_reason: STEP-06 needed vector_only persistence and deterministic Top-K retrieval in local runtime.
change_record: 2026-02-22 implemented ChromaVectorStore + VectorStoreError and normalized vector validation helpers.
updated_at: 2026-02-22T14:13:58.3426562+08:00

module_name: retrieval.retriever (implemented)
file_path: src/retrieval/retriever.py
responsibility: orchestrate vector-only flow (index -> embed -> upsert -> query -> return structured similar_cases).
input_output: input=query_text/top_k and RetrievalDocument list for indexing; output=Top-K retrieval objects for downstream reasoning.
dependencies: src/infra/api_client.py, src/retrieval/vector_store_chroma.py, src/retrieval/document_builder.py.
change_reason: STEP-06 required clear orchestration boundary between API client and vector store with no direct HTTP in retrieval business logic.
change_record: 2026-02-22 implemented VectorOnlyRetriever, RetrieverError, and build_default_vector_only_retriever.
updated_at: 2026-02-22T14:13:58.3426562+08:00

module_name: reasoning.tendency_service (implemented)
file_path: src/reasoning/tendency_service.py
responsibility: decide HSIL/LSIL/Uncertain from retrieval evidence with fixed thresholds, tie handling, and explainable reason output.
input_output: input=similar_cases list(label/similarity) + top_k; output=tendency decision object (tendency/reason/disclaimer); errors=ValueError for invalid top_k.
dependencies: retrieval result schema from src/retrieval/retriever.py.
change_reason: STEP-07 required deterministic tendency decision for ACC-03/ACC-05 with explicit uncertainty boundaries.
change_record: 2026-02-22 implemented infer_tendency, uncertainty thresholds, tie-to-uncertain rule, and shared disclaimer constant.
updated_at: 2026-02-22T14:58:03.8394165+08:00

module_name: cli.main (implemented)
file_path: src/cli/main.py
responsibility: provide local rag-query CLI entry, validate minimal query arguments, orchestrate retrieval+tendency inference, and emit structured JSON output.
input_output: input=CLI args (--case-id, --stain-text/--stain-file, --report-text, --image-paths, --top-k); output=JSON payload with similar_cases/tendency/reason/disclaimer/meta and deterministic exit codes (0 success, 2 argument error, 1 runtime error).
dependencies: src/retrieval/retriever.py, src/reasoning/tendency_service.py, argparse, json, pathlib.
change_reason: STEP-08 requires a stable external interaction contract aligned with PRD and implementation-plan CLI schema.
change_record: 2026-02-22 implemented parse_args/_resolve_stain_text/run_query/main, enforced stain input + top_k + image_paths validations, and added UTF-8 stain-file loading path.
updated_at: 2026-02-22T15:38:17.7809093+08:00

module_name: qa.acceptance_mapping (implemented)
file_path: tests/test_e2e_v1_baseline.py, tests/test_failure_paths.py, docs/manual-acceptance-v1.md
responsibility: provide executable PRD acceptance mapping (ACC-01 to ACC-05), regression failure-path coverage, and manual verification checklist for V1 baseline.
input_output: input=system behaviors from ingestion/retrieval/reasoning/cli/infra layers and simulated error paths; output=deterministic pytest pass/fail signals plus manual acceptance criteria.
dependencies: src/cli/main.py, src/retrieval/retriever.py, src/reasoning/tendency_service.py, src/infra/api_client.py, pytest.
change_reason: STEP-09 required complete QA baseline with traceable acceptance-to-test mapping and diagnosable failure-path assertions.
change_record: 2026-02-22 added ACC baseline e2e tests, failure-path tests (missing input, timeout, empty recall, invalid UTF-8), and manual acceptance checklist; normalized stain-file UTF-8 decode path to argument error.
updated_at: 2026-02-22T16:06:07.3608517+08:00

module_name: milestone.epic_qa
file_path: memory-bank/progress.md, memory-bank/implementation-plan.md, memory-bank/architecture.md
responsibility: mark EPIC-QA completion at STEP-09 and keep progress/architecture milestone state synchronized.
input_output: input=STEP-09 done status and commit linkage; output=milestone completion trace for release readiness.
dependencies: STEP-09 deliverables (tests/test_e2e_v1_baseline.py, tests/test_failure_paths.py, docs/manual-acceptance-v1.md).
change_reason: EPIC-QA milestone reached when STEP-09 moved from in_progress to done.
change_record: 2026-02-22 recorded milestone completion after commit_ref backfill and status closure.
updated_at: 2026-02-22T16:06:07.3608517+08:00

module_name: ux.localization_step10 (implemented, docs-only)
file_path: memory-bank/progress.md, memory-bank/implementation-plan.md, memory-bank/prd.md, memory-bank/tech-stack.md, memory-bank/architecture.md
responsibility: formalize Chinese-friendly and beginner-friendly refactor scope, compatibility guardrails, and execution gate before code changes.
input_output: input=user requirement change ("project-wide Chinese-friendly + beginner-friendly"); output=STEP-10 done with synchronized documentation constraints and execution gate.
dependencies: existing V1 baseline contracts from cli.main, reasoning.tendency_service, and qa.acceptance_mapping.
change_reason: requirement-change/refactor request required documentation synchronization before implementation.
change_record: 2026-02-22 created STEP-10 docs-only gate to prevent cross-step implementation and keep memory-bank artifacts aligned; 2026-02-22 completed docs consistency review and closed STEP-10 as done without src/tests behavior changes.
updated_at: 2026-02-22T16:23:32.7530484+08:00
