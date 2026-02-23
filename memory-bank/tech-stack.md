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

## 1. 当前实际技术栈（V1 已落地）
| 组件 | 作用 | 代码落点 |
|---|---|---|
| Python + conda | 运行环境与开发环境 | 全项目 |
| chromadb | 本地向量持久化与检索 | `src/retrieval/vector_store_chroma.py` |
| httpx | 外部 API 调用 | `src/infra/api_client.py` |
| pytest | 自动化测试 | `tests/` |
| ruff | 代码质量约束（保留策略） | 项目规范 |
| .env + 环境变量 | provider 配置注入 | `src/infra/api_client.py` |

说明：当前检索主链路仍以手写编排为主（`src/retrieval/retriever.py`）。

## 2. 目标技术栈（V2 渐进）
| 目标组件 | 迁移目的 | 迁移阶段 |
|---|---|---|
| langchain / langchain-core | 降低手写编排冗余，统一检索链路抽象 | STEP-12 / STEP-14 |
| LangChain Embeddings | 统一向量化入口 | STEP-14 |
| LangChain VectorStore Adapter | 规范化向量库接入层 | STEP-14 |
| Retriever Adapter（项目内） | 保持输出契约兼容，隔离迁移风险 | STEP-12 / STEP-14 |

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
4. STEP-14：检索主链路渐进迁移到 LangChain。
5. STEP-15：回归验收与文档收口。

## 5. 暂不引入（本阶段）
1. 服务化框架（如 FastAPI）不是本轮目标。
2. 图像向量检索主链路不是本轮目标。
3. 重型工作流编排器（如 Airflow/Celery）不是本轮目标。

## 6. 风险控制
1. 避免一次性全量重写，降低迁移失败风险。
2. 通过 adapter 维持兼容，降低调用方感知变化。
3. 以回归测试通过作为迁移完成标准，而非“框架使用率”本身。
