# Feature-12 LangChain 迁移设计冻结（STEP-12）

## 文档目的
1. 冻结 STEP-12 的接口与数据流设计，作为 STEP-14 编码实现的直接输入。
2. 在不修改现有对外契约的前提下，定义 LangChain 渐进迁移的内部边界。
3. 固化错误透传与错误映射规则，避免迁移期语义退化。

## 范围内
1. Retriever Adapter 内部接口契约与输入输出约束。
2. LangChain 检索结果到 `similar_cases` 的字段映射规则。
3. 检索索引流、查询流的数据流规格与失败路径边界。
4. 与现有 CLI 对外契约兼容的约束声明。

## 范围外
1. 任何运行时代码实现与行为变更。
2. 新增或修改公共接口（CLI 参数、JSON 顶层字段、外部 I/O 契约）。
3. `HSIL | LSIL | Uncertain` 判定逻辑与阈值调整。

## 真源文档
1. `memory-bank/implementation-plan.md`
2. `memory-bank/progress.md`

## 依赖文档
1. `memory-bank/prd.md`
2. `memory-bank/architecture.md`
3. `memory-bank/tech-stack.md`
4. `src/retrieval/retriever.py`
5. `src/cli/main.py`
6. `src/infra/api_client.py`

## 更新触发
1. STEP-14 实施过程中发现本规格存在歧义或不可实现约束时。
2. 对外契约或错误分层策略发生变更时。
3. LangChain 组件选型或模块边界变化时。

## 验收锚点
1. 开发者仅凭本文档即可实现 STEP-14，不需补充决策。
2. 本文档定义的输出字段可直接映射到现有 CLI payload。
3. 错误映射矩阵覆盖超时、鉴权、限流、响应异常、输入异常、未知异常六类路径。

## 更新时间
2026-02-23

## 1. 背景与约束
1. 当前检索主链路由 `VectorOnlyRetriever` 完成，接口形态为 `retrieve(query_text, top_k)`。
2. V2 迁移策略是渐进替换，禁止一次性重写。
3. 对外契约保持不变：`similar_cases/tendency/reason/disclaimer/meta`。
4. 错误分层保持不变：`ApiTimeoutError/ApiAuthError/ApiRateLimitError/ApiResponseError`。

## 2. 接口契约
### 2.1 RetrieverAdapter 协议（内部）
```python
from typing import Protocol

class RetrieverAdapterProtocol(Protocol):
    def index_documents(self, documents: list[RetrievalDocument]) -> None:
        ...

    def retrieve(self, query_text: str, *, top_k: int = 5) -> list[dict[str, object]]:
        ...
```

### 2.2 输入约束
1. `documents` 必须为非空列表，元素符合 `RetrievalDocument` 契约。
2. `query_text` 必须为非空字符串。
3. `top_k` 必须为正整数。

### 2.3 输出约束（retrieve）
1. 返回值是按相似度降序排列的 `list[dict[str, object]]`。
2. 每个元素必须包含字段：
   - `case_id: str`
   - `label: str`
   - `similarity: float`
   - `evidence: str`
   - `metadata: dict[str, object]`
3. `metadata` 至少包含：
   - `case_id`
   - `label`
   - `report_pdf_path`
   - `stain_text_path`

### 2.4 失败行为
1. 输入不合法时，抛出 `RetrieverError`（或适配层等价输入异常）并停止后续调用。
2. 上游 embedding/vector store/langchain 失败时，不吞错，按第 4 章映射后抛出。

## 3. 数据流规格
### 3.1 索引流（Index Flow）
1. 输入：`list[RetrievalDocument]`
2. 处理步骤：
   - 校验输入合法性。
   - 取 `document.content` 列表进行 embedding。
   - 以 `documents + embeddings` 写入向量库。
3. 输出：无（副作用为向量索引更新）。
4. 失败路径：
   - embedding 失败 -> 按错误映射抛出。
   - vectorstore upsert 失败 -> 包装为检索层错误抛出。

### 3.2 查询流（Query Flow）
1. 输入：`query_text`, `top_k`
2. 处理步骤：
   - 校验 `query_text/top_k`。
   - 对 query 执行 embedding。
   - 召回 top-k 文档与分数。
   - 执行字段标准化与兼容映射，输出 `similar_cases` 列表。
3. 输出：`list[dict[str, object]]`（可直接给 CLI payload 使用）。
4. 排序规则：按 `similarity` 降序。
5. 空结果规则：允许返回空列表，不抛异常。

## 4. 错误映射矩阵
| 来源层 | 典型错误 | 目标错误类型 | 说明 |
|---|---|---|---|
| Embedding 调用 | 请求超时 | `ApiTimeoutError` | 保留重试后超时语义 |
| Embedding 调用 | 401/403 | `ApiAuthError` | 保留鉴权失败语义 |
| Embedding 调用 | 429 | `ApiRateLimitError` | 保留限流语义 |
| Embedding/Generation 调用 | 4xx/5xx 非上述类型、响应格式异常 | `ApiResponseError` | 保留响应异常语义 |
| Adapter 输入校验 | 空 query、非法 top_k、空 documents | `RetrieverError` | 本地输入约束失败 |
| LangChain/VectorStore 内部异常 | 未知 runtime 异常 | `ApiResponseError` 或 `RetrieverError` | 若来源是远端调用归并为 `ApiResponseError`，否则 `RetrieverError` |

## 5. 字段映射规范（LangChain -> similar_cases）
| LangChain 结果字段 | 目标字段 | 规则 |
|---|---|---|
| `document.metadata.case_id` | `case_id` | 必填，缺失视为映射失败 |
| `document.metadata.label` | `label` | 必填，缺失视为映射失败 |
| `score` | `similarity` | 转为 `float`，无法转换视为映射失败 |
| `document.page_content` | `evidence` | 取原文内容 |
| `document.metadata` | `metadata` | 透传原 metadata，至少保留四个关键字段 |

映射失败策略：
1. 单条记录关键字段缺失：该条跳过并记录 warning（实现阶段日志化）。
2. 全部记录映射失败：返回空列表并抛出 `RetrieverError`（实现阶段按策略二选一，默认抛错）。

## 6. 兼容性约束
1. `src/cli/main.py` 输出 payload 顶层字段不变：
   - `similar_cases`
   - `tendency`
   - `reason`
   - `disclaimer`
   - `meta`
2. `meta.top_k`、`meta.query_case_id` 保持语义不变。
3. `meta.retrieval_mode` 在迁移阶段仍可使用 `vector_only`，切换 LangChain 后允许为新值，但字段必须保留。
4. 不改 CLI 入参，不改退出码语义。
5. 不改 `tendency_service` 判定逻辑。

## 7. STEP-14 实施清单
1. 新增 `src/retrieval/langchain_retriever.py`（Adapter 等价落点）
   - 实现 `RetrieverAdapterProtocol`。
   - 封装 LangChain 检索调用与结果标准化。
   - 复用 `src/retrieval/metadata_codec.py` 处理 metadata 非标量字段兼容。
2. 修改 `src/retrieval/retriever.py`
   - 保持旧接口可用。
   - 提供迁移期工厂方法，允许切换实现。
3. 评估 `src/cli/main.py`
   - 保持 `run_query` 与 `_build_result_payload` 输出结构不变。
4. 扩展测试
   - 新增 adapter 映射单测。
   - 保留并复用 `tests/test_retriever_topk.py` 的排序和字段断言。
   - 增加错误映射路径用例。
5. 回归门禁
   - 检索主路径行为不倒退。
   - 失败路径错误语义不退化。

## 8. 人工验收清单（STEP-12）
1. 规格是否覆盖接口、数据流、错误边界三要素。
2. 规格是否能直接映射到现有 `cli.main` 输出结构。
3. 规格是否明确列出 STEP-14 文件落点与测试落点。
4. 是否无跨 step 实现内容（仅设计冻结）。
