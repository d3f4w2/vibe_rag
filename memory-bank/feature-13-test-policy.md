# Feature-13 测试策略重构与边界兼容（STEP-13）

## 文档目的
1. 固化 STEP-13 的边界条件矩阵重构结果与风险说明。
2. 记录“保留关键防线 + 合并重复分支”的具体落点，确保可追溯。
3. 为后续 STEP-14/15 回归提供稳定测试基线与回滚依据。

## 范围内
1. 检索链路 metadata 非标量兼容修复（Chroma metadata scalar 限制）。
2. 重复用例合并与关键边界防线保留策略。
3. 测试映射与回归清单（`vibe-rag` 环境）。

## 范围外
1. LangChain 主链路迁移实现（STEP-14 范围）。
2. 对外 CLI 契约变更。
3. `HSIL | LSIL | Uncertain` 判定阈值调整。

## 真源文档
1. `memory-bank/implementation-plan.md`
2. `memory-bank/progress.md`

## 依赖文档
1. `memory-bank/prd.md`
2. `memory-bank/architecture.md`
3. `tests/test_retriever_topk.py`
4. `tests/test_e2e_v1_baseline.py`
5. `tests/test_failure_paths.py`
6. `tests/test_vector_store_chroma_metadata.py`
7. `src/retrieval/vector_store_chroma.py`

## 更新触发
1. STEP-13 测试矩阵调整（保留/合并/删除）发生变化时。
2. Chroma / metadata 行为变化导致兼容策略需要更新时。
3. 回归基线或失败路径语义发生变化时。

## 验收锚点
1. `vibe-rag` 环境下 `python -m pytest -q tests` 全绿。
2. 每条合并/删除分支均有风险说明和替代回归路径。
3. 检索链路返回的 `metadata.image_paths` 等非标量字段可恢复。

## 更新时间
2026-02-23

## Intent
1. 降低重复测试维护成本，同时不削弱高风险路径覆盖。
2. 将 Chroma 对 metadata 标量限制纳入受控兼容策略，避免检索链路因 list/dict 元数据崩溃。

## Scope
1. 覆盖文件：
   - `src/retrieval/vector_store_chroma.py`
   - `tests/test_vector_store_chroma_metadata.py`
   - `tests/test_retriever_topk.py`
   - `tests/test_e2e_v1_baseline.py`
   - `tests/test_failure_paths.py`
2. 保持稳定项：
   - CLI 输出契约不变。
   - 错误分层语义不变。
   - 判定逻辑阈值不变。

## Steps
1. 先新增失败用例，锁定 metadata 非标量值（list/dict）场景。
2. 在向量存储层引入 metadata 编解码兼容逻辑（写入可持久化，查询可恢复）。
3. 合并重复边界用例，保留唯一高价值断言点。
4. 执行受影响子集回归与全量回归，确认行为不回退。

## Tests
### 保留矩阵（高风险防线）
| 类别 | 保留用例 | 目的 |
|---|---|---|
| 向量检索排序 | `tests/test_retriever_topk.py::test_retrieve_top_k_returns_expected_count_and_similarity_order` | 防止召回数量/排序退化 |
| 检索字段完整性 | `tests/test_retriever_topk.py::test_retrieve_top_k_includes_similarity_and_source_metadata` | 确保 `metadata` 关键字段可追溯 |
| metadata 非标量兼容 | `tests/test_vector_store_chroma_metadata.py::test_query_restores_non_scalar_metadata_fields` | 覆盖 list/dict 编解码恢复 |
| E2E 检索烟囱 | `tests/test_e2e_v1_baseline.py::test_acc_01_vector_retrieval_smoke_returns_ranked_traceable_results` | 覆盖真实链路不崩溃 |
| 失败路径语义 | `tests/test_failure_paths.py::test_failure_api_timeout_returns_runtime_error` | 保证 runtime 错误语义稳定 |

### 合并矩阵（去重）
| 原重复点 | 处理策略 | 风险说明 | 替代回归路径 |
|---|---|---|---|
| E2E 中拆分的“top-k 排序”和“字段可追溯”两条独立断言 | 合并为单条烟囱用例（`test_acc_01_vector_retrieval_smoke_returns_ranked_traceable_results`） | 单测失败定位粒度略降 | `tests/test_retriever_topk.py` 保留细粒度排序与字段断言 |
| CLI 缺少 stain 输入在 `test_cli_main.py` 与 `test_failure_paths.py` 双重覆盖 | 从 `test_failure_paths.py` 删除重复断言，保留 `test_cli_main.py::test_cli_requires_stain_text_or_stain_file` | 失败路径文件覆盖面减少 | `test_cli_main.py` + `test_failure_api_timeout_returns_runtime_error` 仍覆盖参数与运行时分层 |

### 删除矩阵
| 删除用例 | 删除原因 | 风险说明 | 替代用例 |
|---|---|---|---|
| `tests/test_failure_paths.py::test_failure_missing_required_stain_input_returns_argument_error` | 与 `test_cli_main.py` 同语义重复 | 仅在同一错误类型上减少一条重复断言 | `tests/test_cli_main.py::test_cli_requires_stain_text_or_stain_file` |
| `tests/test_e2e_v1_baseline.py::test_acc_02_result_contains_traceable_evidence_and_source_fields`（并入 acc_01） | 与 acc_01 前置链路重复，维护成本高 | E2E 粒度减少 | `tests/test_e2e_v1_baseline.py::test_acc_01...` + `tests/test_retriever_topk.py` |

### 回归命令（固定环境）
1. `conda run -n vibe-rag python -m pytest -q tests/test_vector_store_chroma_metadata.py tests/test_retriever_topk.py tests/test_e2e_v1_baseline.py`
2. `conda run -n vibe-rag python -m pytest -q tests`

## Impact
1. 正向影响：
   - 修复 Chroma metadata scalar 限制导致的检索链路失败。
   - 降低测试冗余，提升回归效率。
2. 兼容影响：
   - 不影响 CLI 外部契约与输出结构。
   - 仅增强内部存储层兼容行为。

## Docs to update
1. `memory-bank/progress.md`：STEP-13 状态、测试结果、AI Review 结果。
2. `memory-bank/quick-map.md`：当前焦点状态同步到 `STEP-13 ing`。
3. `memory-bank/implementation-plan.md`：当前执行上下文从待门禁改为执行中。
4. `memory-bank/architecture.md`：记录 STEP-13 里程碑变更原因与模块职责补充。

## Rollback
1. 如兼容逻辑导致 metadata 语义异常，可回滚 `src/retrieval/vector_store_chroma.py` 中编解码函数改动。
2. 回滚后需恢复失败基线说明，并在 STEP-13 中重新标记 blocker 与解除条件。
3. 回滚验证命令：
   - `conda run -n vibe-rag python -m pytest -q tests/test_retriever_topk.py tests/test_e2e_v1_baseline.py`
   - `conda run -n vibe-rag python -m pytest -q tests`
