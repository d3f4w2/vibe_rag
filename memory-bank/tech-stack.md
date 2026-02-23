# Tech Stack（V2，v3.1 对齐）

## 文档目的
1. 明确“当前实际技术栈”和“目标迁移技术栈”的差异。
2. 帮助 AI 与人类快速判断哪些已落地、哪些计划迁移、哪些必须保持不变。
3. 作为架构调整与需求评审的技术边界基线。

## 范围内
1. 当前已落地技术栈、目标技术栈、迁移阶段映射。
2. 迁移期间必须保留项、暂不引入项、风险控制策略。
3. 与 `implementation-plan.md` 的 step 对齐关系。

## 范围外
1. 与当前阶段无关的技术愿望清单。
2. 实现层代码细节与临时调优参数。
3. 业务需求验收条款（由 `prd.md` 管理）。

## 真源文档
1. `C:\Users\ljh\Desktop\workflow\工作流v3.1.txt`

## 依赖文档
1. `memory-bank/prd.md`
2. `memory-bank/architecture.md`
3. `memory-bank/implementation-plan.md`

## 更新触发
1. 技术选型变化、关键依赖变更、迁移阶段调整时。
2. 架构图或 step 计划涉及技术栈映射变化时。
3. 出现框架例外并通过评审时。

## 验收锚点
1. 当前栈与目标栈能映射到明确 step（STEP-12~15）。
2. 必须保留项在迁移期间无语义退化。
3. 暂不引入项明确且与 PRD 范围外一致。

## 更新时间
2026-02-23

## 1. 当前实际技术栈（V2，STEP-14 执行中）
| 组件 | 作用 | 代码落点 |
|---|---|---|
| Python + conda | 运行环境与开发环境 | 全项目 |
| chromadb | 本地向量持久化与检索 | `src/retrieval/vector_store_chroma.py` |
| httpx | 外部 API 调用 | `src/infra/api_client.py` |
| langchain / langchain-core | 检索编排主链路抽象 | `src/retrieval/langchain_retriever.py` |
| langchain-community | LangChain 社区组件集 | `src/retrieval/langchain_retriever.py` |
| langchain-chroma | LangChain 与 Chroma 对接 | `src/retrieval/langchain_retriever.py` |
| pytest | 自动化测试 | `tests/` |
| ruff | 代码质量约束（保留策略） | 项目规范 |
| .env + 环境变量 | provider 配置注入 | `src/infra/api_client.py` |

说明：默认检索工厂已切换到 LangChain 实现（`src/retrieval/retriever.py` -> `src/retrieval/langchain_retriever.py`），`VectorOnlyRetriever` 仍保留用于兼容测试与回退。

## 1.1 关键版本基线（vibe-rag，2026-02-23）
| 组件 | 版本 | 说明 |
|---|---:|---|
| chromadb | 1.5.1 | 当前向量数据库实现 |
| httpx | 0.28.1 | API 客户端传输层 |
| langchain | 1.2.10 | 检索链路主框架 |
| langchain-core | 1.2.14 | LangChain 核心接口 |
| langchain-community | 0.4.1 | 社区扩展组件 |
| langchain-chroma | 1.1.0 | Chroma 对接适配 |
| langsmith | 0.7.6 | LangChain 观测依赖（随环境存在） |

注：其余运行时库版本以人类提供的 `vibe-rag` 环境清单为准。

## 2. 迁移目标技术栈（V2 渐进）
| 目标组件 | 迁移目的 | 阶段 |
|---|---|---|
| langchain / langchain-core | 统一检索链路抽象，降低手写编排冗余 | STEP-12 设计冻结，STEP-14 已执行 |
| LangChain Embeddings Adapter（项目内） | 复用现有 `ApiClient` 接口进行向量化 | STEP-14 |
| langchain-chroma | 统一 Chroma 检索入口 | STEP-14 |
| metadata codec（项目内） | 维持 metadata 非标量字段兼容 | STEP-13 已落地，STEP-14 复用 |

## 3. 必须保留（迁移期间不变）
1. 错误分层语义：
   - `ApiTimeoutError`
   - `ApiAuthError`
   - `ApiRateLimitError`
   - `ApiResponseError`
2. 对外 CLI 契约与退出码策略保持稳定。
3. `HSIL | LSIL | Uncertain` 判定规则在 V2 前半程不改。
4. 状态机治理写入口径保持 `todo|ing|blocked|待提交|done`。

## 4. 迁移路线（与 step 对齐）
1. STEP-11：文档清晰化（图注增强、提交时间制）。
2. STEP-12：冻结接口与数据流设计（不写代码实现）。
3. STEP-13：边界条件矩阵与测试策略重构。
4. STEP-14：检索主链路迁移到 LangChain（执行中，默认工厂已切换）。
5. STEP-15：回归验收与文档收口。

## 5. 暂不引入（本阶段）
1. 服务化框架（如 FastAPI）不是本轮目标。
2. 图像向量检索主链路不是本轮目标。
3. 重型工作流编排器（如 Airflow/Celery）不是本轮目标。

## 6. 风险控制
1. 避免一次性全量重写，降低迁移失败风险。
2. 通过 adapter 维持兼容，降低调用方感知变化。
3. 以回归测试通过作为迁移完成标准，而非“框架使用率”本身。
