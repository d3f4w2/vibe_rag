# Implementation Plan（V1 基础版，Step-Based + TDD）

## 0. Scope and Guardrails
1. 本计划仅覆盖 `memory-bank/prd.md` 中的 V1 基础能力，不扩展到服务化、图像向量检索或在线学习。
2. 所有 step 必须按 TDD 顺序执行：先写失败测试 -> 最小实现通过 -> 重构不改行为。
3. 未收到明确指令 `start next step` 前，不得进入下一 step。
4. 每个 step 完成后必须更新 `memory-bank/progress.md`（若文件缺失，先补最小模板）。
5. 若出现 blocker，立即将当前 step 标记为 `blocked`，并记录解除条件。
6. 决策锁定（本版必须执行）：
   - 门禁口令统一为 `start next step`。
   - 执行阶段使用真实 API；mock 仅可用于局部单测，不可替代主流程验证。
   - `Uncertain` 判定固定为双条件：`top1_similarity < 0.60` 且 `Top-K 多数标签占比 < 0.60`。
   - 若 Top-K 标签票数并列第一（tie），直接返回 `Uncertain`。
   - CLI 输出格式固定为结构化 JSON。
   - API 访问统一封装在 `src/infra/api_client.py`。
7. 若需要变更上述锁定项，必须先按规则提问确认，再修改计划文档。

## 1. Step List（Small-Grained）

### Step 01
1. Step ID: `STEP-01`
2. Epic ID: `EPIC-INGESTION`
3. 目标（Goal）:
   - 定义病例元数据结构和输入输出契约，覆盖 `case_id`、`label`、路径、报告时间、文本字段。
4. 测试（先写失败测试）:
   - 新增测试：配置/模型初始化时，缺少必填字段应抛出明确错误。
   - 新增测试：`label` 仅允许 `HSIL | LSIL`。
5. 失败测试结果摘要（失败原因/关键断言）:
   - 失败原因：尚未定义结构化模型与校验规则。
   - 关键断言：非法标签、缺失字段被拒绝。
6. 最小实现（通过测试）:
   - 实现最小数据模型与校验逻辑，不引入额外业务流程。
7. 重构（不改行为）:
   - 将模型定义与工具函数拆分到独立模块，清理重复校验逻辑。
8. 完成标准（Done Criteria）:
   - 模型测试全部通过，且错误信息可定位字段。
9. 人工验证方法（Manual Test）:
   - 人工构造合法/非法样例，确认校验行为与报错一致。
10. 产出物（修改文件/命令/结果）:
   - 文件：`src/models/case_record.py`、`tests/test_case_record_schema.py`
   - 命令：`pytest -k case_record_schema`
   - 结果：schema 校验测试通过。

### Step 02
1. Step ID: `STEP-02`
2. Epic ID: `EPIC-INGESTION`
3. 目标（Goal）:
   - 实现数据目录扫描，识别 `data/HSIL/*`、`data/LSIL/*` 下合法病例目录。
4. 测试（先写失败测试）:
   - 新增测试：合法目录被发现并映射正确标签。
   - 新增测试：目录结构不完整时返回可追踪错误。
5. 失败测试结果摘要（失败原因/关键断言）:
   - 失败原因：尚无扫描器，无法返回病例清单。
   - 关键断言：每个病例必须包含 `5 JPG + 1 PDF + 1 TXT`。
6. 最小实现（通过测试）:
   - 实现目录扫描与文件完整性检查，返回结构化病例列表。
7. 重构（不改行为）:
   - 抽取路径解析函数，统一错误对象格式。
8. 完成标准（Done Criteria）:
   - 目录扫描对现有样本可稳定输出病例清单和错误列表。
9. 人工验证方法（Manual Test）:
   - 在测试数据中故意删减一个文件，确认系统能识别并报告。
10. 产出物（修改文件/命令/结果）:
   - 文件：`src/ingestion/case_scanner.py`、`tests/test_case_scanner.py`
   - 命令：`pytest -k case_scanner`
   - 结果：扫描与结构校验测试通过。

### Step 03
1. Step ID: `STEP-03`
2. Epic ID: `EPIC-INGESTION`
3. 目标（Goal）:
   - 实现文本清洗，保证 UTF-8 读取并移除 `0x7F` 控制字符。
4. 测试（先写失败测试）:
   - 新增测试：包含 `0x7F` 的文本被清洗。
   - 新增测试：UTF-8 读取失败时返回明确错误而非静默吞掉。
5. 失败测试结果摘要（失败原因/关键断言）:
   - 失败原因：当前未实现文本清洗器。
   - 关键断言：输出文本不包含 `0x7F`，且保持原语义顺序。
6. 最小实现（通过测试）:
   - 实现最小清洗函数和读取流程，输出标准化 `stain_text`。
7. 重构（不改行为）:
   - 将清洗规则配置化（仅保留当前必需规则），便于后续扩展。
8. 完成标准（Done Criteria）:
   - 文本清洗测试通过，且可被后续索引流程直接调用。
9. 人工验证方法（Manual Test）:
   - 打开一个包含异常字符的 `着色情况.txt`，确认清洗前后差异可解释。
10. 产出物（修改文件/命令/结果）:
   - 文件：`src/ingestion/text_cleaner.py`、`tests/test_text_cleaner.py`
   - 命令：`pytest -k text_cleaner`
   - 结果：控制字符清洗测试通过。

### Step 04
1. Step ID: `STEP-04`
2. Epic ID: `EPIC-INGESTION`
3. 目标（Goal）:
   - 解析 PDF 文件名时间戳并生成 `JSONL` 元数据，供后续检索索引使用。
4. 测试（先写失败测试）:
   - 新增测试：合法文件名可正确解析 `YYYYMMDDHHMMSS`。
   - 新增测试：非法文件名时间戳返回可诊断错误。
   - 新增测试：输出 `JSONL` 字段完整且可复读。
5. 失败测试结果摘要（失败原因/关键断言）:
   - 失败原因：尚无时间解析与元数据序列化模块。
   - 关键断言：每条记录包含 `case_id`、`label`、路径、时间。
6. 最小实现（通过测试）:
   - 实现时间解析器与 `JSONL` 写入器，保证顺序和字段一致性。
7. 重构（不改行为）:
   - 提取序列化层，降低扫描器与存储层耦合。
8. 完成标准（Done Criteria）:
   - `JSONL` 可作为后续索引输入，且字段契约稳定。
9. 人工验证方法（Manual Test）:
   - 随机抽查多条 `JSONL` 记录，核对路径与时间是否与源文件一致。
10. 产出物（修改文件/命令/结果）:
   - 文件：`src/ingestion/report_time_parser.py`、`src/ingestion/metadata_store.py`、`tests/test_metadata_store.py`
   - 命令：`pytest -k metadata_store`
   - 结果：元数据生成测试通过。

### Step 05
1. Step ID: `STEP-05`
2. Epic ID: `EPIC-RETRIEVAL`
3. 目标（Goal）:
   - 构建检索文档对象（以 `stain_text` 为主，`report_text` 可选），准备向量化输入。
4. 测试（先写失败测试）:
   - 新增测试：`report_text` 缺失时不阻塞流程。
   - 新增测试：文档对象携带可追溯元数据（来源病例、路径、时间）。
5. 失败测试结果摘要（失败原因/关键断言）:
   - 失败原因：尚未定义检索文档拼装规则。
   - 关键断言：最小输入集合可构建可检索文档。
6. 最小实现（通过测试）:
   - 实现文档拼装函数，输出统一检索输入结构。
7. 重构（不改行为）:
   - 统一字段命名并抽离公共映射函数。
8. 完成标准（Done Criteria）:
   - 文档构建可覆盖“仅 stain_text”与“stain + report”两种情况。
9. 人工验证方法（Manual Test）:
   - 人工打印单条文档对象，核对内容与元数据完整性。
10. 产出物（修改文件/命令/结果）:
   - 文件：`src/retrieval/document_builder.py`、`tests/test_document_builder.py`
   - 命令：`pytest -k document_builder`
   - 结果：文档构建测试通过。

### Step 06
1. Step ID: `STEP-06`
2. Epic ID: `EPIC-RETRIEVAL`
3. 目标（Goal）:
   - 实现 `vector_only` 检索链路：向量化 -> Chroma 持久化 -> Top-K 召回。
   - 通过 `src/infra/api_client.py` 统一调用 embedding API，并统一错误处理。
4. 测试（先写失败测试）:
   - 新增测试：Top-K 返回数量与排序符合预期。
   - 新增测试：召回结果包含相似度和来源元数据。
   - 新增测试：`src/infra/api_client.py` 对超时、401、429、5xx 错误做统一映射。
   - 新增测试：在真实 API 配置下可完成一次最小 embedding 集成调用。
5. 失败测试结果摘要（失败原因/关键断言）:
   - 失败原因：尚未接入 Chroma 检索实现与统一 API 客户端。
   - 关键断言：`top_k` 参数生效，检索结果结构稳定，API 异常类型可判别。
6. 最小实现（通过测试）:
   - 实现 `src/infra/api_client.py`，固定接口：
     - `embed_texts(texts: list[str]) -> list[list[float]]`
     - `generate_reasoning(prompt: str) -> str`
   - 实现错误类型：`ApiTimeoutError`、`ApiAuthError`、`ApiRateLimitError`、`ApiResponseError`。
   - 检索模块仅通过该客户端取向量，不直接访问 HTTP。
7. 重构（不改行为）:
   - 抽象存储接口，隔离 Chroma 细节，降低检索层耦合。
8. 完成标准（Done Criteria）:
   - 单机本地可完成索引构建与 Top-K 检索闭环。
   - `vector_only` 模式完整可用，真实 API 路径通过。
   - API 超时/鉴权/限流错误可被明确捕获并上抛。
9. 人工验证方法（Manual Test）:
   - 使用有效 API Key 执行一次检索，确认返回结构与召回数量正确。
   - 使用无效 API Key 执行一次检索，确认抛出 `ApiAuthError` 并记录可追踪日志。
10. 产出物（修改文件/命令/结果）:
   - 文件：`src/infra/api_client.py`、`src/retrieval/vector_store_chroma.py`、`src/retrieval/retriever.py`、`tests/test_api_client.py`、`tests/test_retriever_topk.py`
   - 命令：`pytest -k "api_client or retriever_topk"`
   - 结果：检索与 API 客户端测试通过。

### Step 07
1. Step ID: `STEP-07`
2. Epic ID: `EPIC-REASONING`
3. 目标（Goal）:
   - 基于召回证据生成 `tendency`（`HSIL | LSIL | Uncertain`）与简短理由。
   - 固化判定规则：
     - 设 `majority_ratio = max(HSIL_count, LSIL_count) / top_k`
     - 若 `top1_similarity < 0.60` 且 `majority_ratio < 0.60`，则 `Uncertain`
     - 若 `HSIL_count == LSIL_count`（并列第一），则 `Uncertain`
     - 其余情况按多数标签输出 `HSIL` 或 `LSIL`
4. 测试（先写失败测试）:
   - 新增测试：`top1_similarity < 0.60` 且多数占比 `< 0.60` 时输出 `Uncertain`。
   - 新增测试：标签并列第一时输出 `Uncertain`。
   - 新增测试：满足多数标签且证据充分时输出对应 `HSIL/LSIL`。
   - 新增测试：输出必须包含 `tendency`、`reason`、`disclaimer`。
5. 失败测试结果摘要（失败原因/关键断言）:
   - 失败原因：尚无可计算的倾向判定与解释逻辑。
   - 关键断言：低证据或标签分散时，不允许强行给出确定倾向。
6. 最小实现（通过测试）:
   - 实现阈值驱动的最小判定策略与解释模板。
7. 重构（不改行为）:
   - 将阈值和文案模板配置化，避免硬编码分散。
8. 完成标准（Done Criteria）:
   - 输出结构满足 PRD 最小输出集合。
   - `Uncertain` 判定在阈值边界和并列边界行为稳定。
9. 人工验证方法（Manual Test）:
   - 使用高证据样本、低证据样本、标签并列样本分别验证输出。
10. 产出物（修改文件/命令/结果）:
   - 文件：`src/reasoning/tendency_service.py`、`tests/test_tendency_service.py`
   - 命令：`pytest -k tendency_service`
   - 结果：倾向与解释测试通过。

### Step 08
1. Step ID: `STEP-08`
2. Epic ID: `EPIC-CLI`
3. 目标（Goal）:
   - 提供本地 CLI 入口，接收最小输入并输出可追溯检索结果。
   - 固定命令契约为 `rag-query`（开发期可由 `python -m src.cli.main` 触发该命令）。
4. 测试（先写失败测试）:
   - 新增测试：CLI 参数校验。
   - 新增测试：`--stain-text` 与 `--stain-file` 至少提供一个，且不可同时缺失。
   - 新增测试：成功路径输出结构化 JSON，字段包含 `similar_cases`、`tendency`、`reason`、`disclaimer`。
5. 失败测试结果摘要（失败原因/关键断言）:
   - 失败原因：尚无统一 CLI 入口、参数契约与 JSON 输出约束。
   - 关键断言：输出字段命名必须与 PRD 对齐。
6. 最小实现（通过测试）:
   - CLI 输入参数固定：
     - `--case-id` 可选
     - `--stain-text` 可选
     - `--stain-file` 可选
     - `--report-text` 可选
     - `--image-paths` 可选（最多 5）
     - `--top-k` 默认 5
   - 输出固定为 JSON，对象包含：
     - `similar_cases`（数组）
     - `tendency`（字符串）
     - `reason`（字符串）
     - `disclaimer`（字符串）
     - `meta`（对象，含 `top_k`、`retrieval_mode`、`query_case_id`）
7. 重构（不改行为）:
   - 拆分参数解析、流程编排、输出序列化层。
8. 完成标准（Done Criteria）:
   - 本地命令可完成端到端查询并输出合法 JSON。
9. 人工验证方法（Manual Test）:
   - 执行一次有效命令，检查 JSON 字段完整。
   - 执行一次缺失必填输入命令，检查错误提示与退出码。
10. 产出物（修改文件/命令/结果）:
   - 文件：`src/cli/main.py`、`tests/test_cli_main.py`
   - 命令：`pytest -k cli_main`
   - 结果：CLI 行为测试通过。

### Step 09
1. Step ID: `STEP-09`
2. Epic ID: `EPIC-QA`
3. 目标（Goal）:
   - 完成 V1 回归测试与失败场景覆盖，形成可执行验收基线。
4. 测试（先写失败测试）:
   - 新增测试：数据缺失、API 超时、空召回、异常编码等路径。
   - 新增测试：端到端回归测试覆盖 PRD 验收标准 1-5。
   - 新增测试：`src/infra/api_client.py` 的重试与错误映射在回归链路中可观察。
5. 失败测试结果摘要（失败原因/关键断言）:
   - 失败原因：尚未覆盖关键异常路径与完整验收断言。
   - 关键断言：异常路径可解释、可追溯，不破坏主流程稳定性。
6. 最小实现（通过测试）:
   - 补齐错误处理、日志关键字段与必要回退分支。
   - 建立 PRD 验收标准与测试用例的一一映射。
7. 重构（不改行为）:
   - 统一错误码/日志字段命名，清理重复断言工具。
8. 完成标准（Done Criteria）:
   - 自动化测试通过，且可映射至 PRD V1 验收标准。
   - 验收映射文档可追踪每条标准对应测试。
9. 人工验证方法（Manual Test）:
   - 按验收清单逐项人工演练，并记录成功判定。
10. 产出物（修改文件/命令/结果）:
   - 文件：`tests/test_e2e_v1_baseline.py`、`tests/test_failure_paths.py`、`docs/manual-acceptance-v1.md`
   - 命令：`pytest`
   - 结果：全量测试通过并产出验收记录。

## 2. PRD 验收映射（固定）
| PRD 验收标准 | 测试用例 ID | 测试文件 |
|---|---|---|
| 1. 合法输入返回 Top-K 相似病例 | `ACC-01` | `tests/test_retriever_topk.py` |
| 2. 返回证据片段且可定位来源病例 | `ACC-02` | `tests/test_e2e_v1_baseline.py` |
| 3. 输出 `HSIL/LSIL/Uncertain` 倾向与理由 | `ACC-03` | `tests/test_tendency_service.py` |
| 4. 文本清洗稳定处理 `0x7F` | `ACC-04` | `tests/test_text_cleaner.py` |
| 5. 证据不足必须返回 `Uncertain` | `ACC-05` | `tests/test_tendency_service.py` |

## 3. Step Execution Gate
1. 当前文档仅定义执行计划，不代表自动进入任一步骤实现。
2. 必须由人类显式发出 `start next step` 才允许从当前 step 进入下一 step。
3. 未收到该指令时，允许做的动作仅限：读取文档、澄清需求、更新计划文本。
4. 当前执行步以 `memory-bank/progress.md` 为准；STEP-10 已完成 docs-only 文档同步并收口为 `done`。

## 4. Step 10（文档同步门禁，docs-only）

### Step 10
1. Step ID: `STEP-10`
2. Epic ID: `EPIC-UX-LOCALIZATION`
3. 目标（Goal）:
   - 将当前任务切换为“中文友好 + 新手友好”重构的正式执行入口。
   - 仅更新 memory-bank 相关文档，锁定后续实现边界与兼容策略。
4. 测试（先写失败测试）:
   - 文档步骤，无代码测试；通过一致性审查验证。
5. 失败测试结果摘要（失败原因/关键断言）:
   - 不适用（docs-only）。
6. 最小实现（通过测试）:
   - 更新 `progress.md`，完成 `STEP-10` 并标记 `done`。
   - 更新 `implementation-plan.md`、`prd.md`、`tech-stack.md`、`architecture.md` 的 Step10 对齐条目。
7. 重构（不改行为）:
   - 统一术语：中文优先 + 英文兼容关键字。
   - 明确“本轮不改代码”的执行边界，避免跨步实现。
8. 完成标准（Done Criteria）:
   - `STEP-10` 在 `progress.md` 中为 `done`。
   - 相关文档均包含 Step10 目标、范围、兼容与非目标约束。
   - 未产生 `src/` 或 `tests/` 的行为变更。
9. 人工验证方法（Manual Test）:
   - 检查 `progress/implementation-plan/prd/tech-stack/architecture` 术语与范围是否一致。
   - 检查 `STEP-10` 未越级进入 `STEP-11`。
10. 产出物（修改文件/命令/结果）:
   - 文件：`memory-bank/progress.md`、`memory-bank/implementation-plan.md`、`memory-bank/prd.md`、`memory-bank/tech-stack.md`、`memory-bank/architecture.md`
   - 命令：文档核对（`git diff -- memory-bank/*`）
   - 结果：完成 Step10 文档同步门禁并收口为 done，不执行代码实现。
