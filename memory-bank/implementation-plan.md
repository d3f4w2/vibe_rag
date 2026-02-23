# Implementation Plan（V2 重构版，Step-Based + TDD）

## 0. Scope and Guardrails
1. 本计划基于 V1 已完成状态，聚焦“清晰文档 + LangChain 渐进迁移”。
2. 门禁口令固定：`start next step`。
3. 未收到门禁口令前，不得进入下一 step，不得跨 step 提前实现。
4. 状态枚举固定为：`todo` / `ing` / `blocked` / `done` / `待提交`。
5. blocker 处理固定输出：
   - `blocker_description`
   - `impact_scope`
   - `unblock_conditions`
   - `suggested_decision`
6. V2 决策锁定：
   - LangChain 渐进替换，不做一次性全面重写。
   - CLI 输出契约保持兼容（`similar_cases/tendency/reason/disclaimer/meta`）。
   - `HSIL | LSIL | Uncertain` 判定阈值在 V2 前半程不变。
   - 错误分层（`ApiTimeoutError/ApiAuthError/ApiRateLimitError/ApiResponseError`）保留。

## 1. 文档清晰化规范（STEP-11 强制）
1. `architecture.md`：
   - 每个图节点必须包含“脚本路径 + 中文职责注释”。
   - 图中节点与模块职责表必须一一对应。
2. `progress.md`：
   - 使用 `提交时间` 字段替代 `更新时间`。
   - 规则：`已提交=✓` 才能写提交时间，`已提交=✗` 必须写 `-`。
3. 五个必读文件（`architecture/prd/implementation-plan/tech-stack/progress`）术语统一。

## 2. 当前执行步（唯一）
1. `current_step_id`: `STEP-11`（待提交）
2. `goal`: 完成文档清晰化修订并等待本次 commit 收口。
3. `selection_reason`: 当前存在 `待提交` step，按规则先收口，不进入 `STEP-12`。

## 3. V2 Step List

### Step 11
1. Step ID: `STEP-11`
2. Step Order: `11`
3. Epic ID: `EPIC-V2-DOCS`
4. 目标（Goal）:
   - 完成文档结构重构，降低冗余并提升可读性。
   - 架构图节点内中文职责注释完整。
   - 进度表使用提交时间规则。
5. 测试策略:
   - 自动化测试：不执行（docs-only）。
   - AI ReviewCode：检查文档间一致性、字段规则一致性。
6. 完成标准（Done Criteria）:
   - 五个必读文件完成同步修订。
   - `progress.md` 不再使用 `更新时间` 列。
   - `architecture.md` 三张图均带中文职责注释。
7. 产出物:
   - `memory-bank/progress.md`
   - `memory-bank/architecture.md`
   - `memory-bank/prd.md`
   - `memory-bank/tech-stack.md`
   - `memory-bank/implementation-plan.md`

### Step 12
1. Step ID: `STEP-12`
2. Step Order: `12`
3. Epic ID: `EPIC-V2-LANGCHAIN-DESIGN`
4. 目标（Goal）:
   - 冻结 LangChain 渐进迁移设计，不写实现代码。
5. 范围:
   - 定义 Retriever Adapter 边界。
   - 定义 LangChain Document 与当前输出结构转换契约。
   - 定义错误透传与错误映射边界。
6. 完成标准:
   - 输出可直接编码的“接口与数据流规格”。
7. 门禁:
   - 仅在收到 `start next step` 后执行。

### Step 13
1. Step ID: `STEP-13`
2. Step Order: `13`
3. Epic ID: `EPIC-V2-TEST-POLICY`
4. 目标（Goal）:
   - 对边界条件做“保留关键防线 + 合并重复分支”的测试策略重构。
5. 范围:
   - 形成边界条件矩阵（保留/合并/删除候选）。
   - 更新测试映射（不削弱高风险路径）。
6. 完成标准:
   - 每个拟删除/合并分支都有风险说明与回归用例。
7. 门禁:
   - 仅在收到 `start next step` 后执行。

### Step 14
1. Step ID: `STEP-14`
2. Step Order: `14`
3. Epic ID: `EPIC-V2-RETRIEVAL-REFACTOR`
4. 目标（Goal）:
   - 渐进迁移检索主链路到 LangChain（先 retrieval）。
5. 范围:
   - 迁移 `retrieval` 编排与向量检索对接。
   - 保持 CLI 输出契约兼容。
   - 保留错误分层可定位性。
6. 完成标准:
   - 关键回归测试通过，检索行为与结构不倒退。
7. 门禁:
   - 仅在收到 `start next step` 后执行。

### Step 15
1. Step ID: `STEP-15`
2. Step Order: `15`
3. Epic ID: `EPIC-V2-QA`
4. 目标（Goal）:
   - 完成 V2 回归、验收映射与文档收口。
5. 范围:
   - 自动化回归。
   - AI ReviewCode 与验收清单同步。
   - milestone 达成后回填 architecture 变更记录。
6. 完成标准:
   - V2 验收项可追溯到测试与文档，状态收口为 `done`。
7. 门禁:
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
1. 当前仅执行 STEP-11 文档修订与收口。
2. AI 可见后续步骤内容，但不得跨 step 提前实现。
3. only executing current step scope.

