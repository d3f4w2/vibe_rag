# Implementation Plan（V2，v3.1 对齐）

## 文档目的
1. 将 V2 目标拆解为可执行、可验收、可回填的 step 列表。
2. 固化门禁规则，确保“一会话一步、不得跨 step”。
3. 为 `progress.md` 提供唯一 step 计划真源。

## 范围内
1. step 清单（ID、顺序、目标、范围、完成标准、门禁）。
2. 状态机与 blocker 生命周期口径。
3. 里程碑（`epic_id`）定义与验收路径。

## 范围外
1. 具体代码实现与临时调试命令。
2. 架构细节图与技术选型长文说明。
3. 独立任务轨道的过程管理。

## 真源文档
1. `C:\Users\ljh\Desktop\workflow\工作流v3.1.txt`
2. `memory-bank/progress.md`

## 依赖文档
1. `memory-bank/quick-map.md`
2. `memory-bank/prd.md`
3. `memory-bank/architecture.md`
4. `memory-bank/tech-stack.md`

## 更新触发
1. 需求边界变化、重构、里程碑拆分调整时。
2. step 完成标准、门禁规则、依赖关系发生变化时。
3. 与 `progress.md` 的 step 映射不一致时。

## 验收锚点
1. 每个 step 具备明确完成标准，能直接落地执行。
2. 门禁口令与会话规则明确：`start next step` + `/new`。
3. `progress.md` 与本计划在 step 顺序和状态口径上无冲突。

## 更新时间
2026-02-23

## 1. Scope and Guardrails
1. 本计划基于 V1 已完成状态，聚焦“清晰文档 + LangChain 渐进迁移”。
2. 门禁口令固定：`start next step`。
3. 会话硬门禁：
   - 一个会话最多执行一个 step。
   - 未收到 `start next step` 前，不得进入下一 step。
   - 进入下一 step 前，必须 `/new` 新会话。
4. 写入状态枚举固定为：`todo` / `ing` / `blocked` / `待提交` / `done`。
5. 迁移兼容：读取时若出现 `in_progress`，按 `ing` 处理；写入统一 v3.1 状态。
6. blocker 处理固定输出：
   - `blocker_description`
   - `impact_scope`
   - `unblock_conditions`
   - `suggested_decision`
7. V2 决策锁定：
   - LangChain 渐进替换，不做一次性全面重写。
   - CLI 输出契约保持兼容（`similar_cases/tendency/reason/disclaimer/meta`）。
   - `HSIL | LSIL | Uncertain` 判定阈值在 V2 前半程不变。
   - 错误分层（`ApiTimeoutError/ApiAuthError/ApiRateLimitError/ApiResponseError`）保留。

## 2. 当前执行上下文（唯一）
1. 项目轨道 `current_step_id`: `STEP-15`（待提交）。
2. `goal`: 完成 V2 回归验收与文档收口。
3. `selection_reason`: `STEP-14` 已以 commit `d7bdcc0` 收口完成；当前按规则选择最小 `todo` 为 `STEP-15`，并已完成自动化回归（55 passed）与 AI Review。
4. 执行约束：仅执行 `STEP-15` 范围，不跨 step 提前实现；当前等待人类 commit 后回填 `commit_ref`。

## 3. V2 Step List

### Step 11
1. Step ID: `STEP-11`
2. Step Order: `11`
3. Epic ID: `EPIC-V2-DOCS`
4. 目标（Goal）：
   - 完成文档结构重构，降低冗余并提升可读性。
   - 架构图节点内中文职责注释完整。
   - 进度表使用提交时间规则。
5. 测试策略：
   - 自动化测试：不执行（docs-only）。
   - AI ReviewCode：检查文档间一致性、字段规则一致性。
6. 完成标准（Done Criteria）：
   - 五个必读文件完成同步修订。
   - `progress.md` 不再使用 `更新时间` 列。
   - `architecture.md` 三张图均带中文职责注释。
7. 产出物：
   - `memory-bank/progress.md`
   - `memory-bank/architecture.md`
   - `memory-bank/prd.md`
   - `memory-bank/tech-stack.md`
   - `memory-bank/implementation-plan.md`

### Step 12
1. Step ID: `STEP-12`
2. Step Order: `12`
3. Epic ID: `EPIC-V2-LANGCHAIN-DESIGN`
4. 目标（Goal）：
   - 冻结 LangChain 渐进迁移设计，不写实现代码。
5. 范围：
   - 定义 Retriever Adapter 边界。
   - 定义 LangChain Document 与当前输出结构转换契约。
   - 定义错误透传与错误映射边界。
6. 完成标准：
   - 输出可直接编码的“接口与数据流规格”。
7. 门禁：
   - 仅在收到 `start next step` 后执行。

### Step 13
1. Step ID: `STEP-13`
2. Step Order: `13`
3. Epic ID: `EPIC-V2-TEST-POLICY`
4. 目标（Goal）：
   - 对边界条件做“保留关键防线 + 合并重复分支”的测试策略重构。
5. 范围：
   - 形成边界条件矩阵（保留/合并/删除候选）。
   - 更新测试映射（不削弱高风险路径）。
6. 完成标准：
   - 每个拟删除/合并分支都有风险说明与回归用例。
7. 门禁：
   - 仅在收到 `start next step` 后执行。

### Step 14
1. Step ID: `STEP-14`
2. Step Order: `14`
3. Epic ID: `EPIC-V2-RETRIEVAL-REFACTOR`
4. 目标（Goal）：
   - 渐进迁移检索主链路到 LangChain（先 retrieval）。
5. 范围：
   - 迁移 `retrieval` 编排与向量检索对接。
   - 保持 CLI 输出契约兼容。
   - 保留错误分层可定位性。
6. 完成标准：
   - 关键回归测试通过，检索行为与结构不倒退。
7. 门禁：
   - 仅在收到 `start next step` 后执行。
8. 环境基线（执行约束）：
   - 运行与测试使用 conda 环境：`vibe-rag`。
   - 关键依赖版本：`chromadb==1.5.1`、`langchain==1.2.10`、`langchain-core==1.2.14`、`langchain-community==0.4.1`、`langchain-chroma==1.1.0`、`httpx==0.28.1`。

### Step 15
1. Step ID: `STEP-15`
2. Step Order: `15`
3. Epic ID: `EPIC-V2-QA`
4. 目标（Goal）：
   - 完成 V2 回归、验收映射与文档收口。
5. 范围：
   - 自动化回归。
   - AI ReviewCode 与验收清单同步。
   - milestone 达成后回填 architecture 变更记录。
6. 完成标准：
   - V2 验收项可追溯到测试与文档，状态收口为 `done`。
7. 门禁：
   - 仅在收到 `start next step` 后执行。

## 4. 里程碑定义
1. 使用 `epic_id` 时，同一 `epic_id` 下全部步骤完成即达成里程碑。
2. 本计划里程碑：
   - `EPIC-V2-DOCS`: STEP-11 完成
   - `EPIC-V2-LANGCHAIN-DESIGN`: STEP-12 完成
   - `EPIC-V2-TEST-POLICY`: STEP-13 完成
   - `EPIC-V2-RETRIEVAL-REFACTOR`: STEP-14 完成
   - `EPIC-V2-QA`: STEP-15 完成

## 5. 执行边界（当前轮）
1. 项目轨道已完成 `STEP-15` 收口范围（自动化回归、AI Review、验收映射、文档回填），当前处于 `待提交`。
2. AI 可见后续步骤内容，但不得跨 step 提前实现。
3. only executing current step scope.
