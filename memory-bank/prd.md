# PRD：宫颈阴道镜病例检索 RAG（V2 阶段）

## 文档目的
1. 定义 V2 阶段需求边界、验收口径和非目标。
2. 为 `implementation-plan.md` 与 `progress.md` 提供产品层真源。
3. 避免实现过程中需求漂移与验收歧义。

## 范围内
1. V2 阶段目标（LangChain 渐进迁移 + 文档治理强化）。
2. 对外契约稳定项（CLI 输出结构、错误分层语义）。
3. 阶段验收标准与主要风险应对。

## 范围外
1. 具体实现代码、临时脚本与调试命令。
2. 与当前阶段无关的服务化、图像检索、重型编排系统扩展。
3. 逐步执行日志（交由 `progress.md` 管理）。

## 真源文档
1. `C:\Users\ljh\Desktop\workflow\工作流v3.1.txt`

## 依赖文档
1. `memory-bank/quick-map.md`
2. `memory-bank/implementation-plan.md`
3. `memory-bank/progress.md`
4. `memory-bank/architecture.md`
5. `memory-bank/tech-stack.md`

## 更新触发
1. 验收标准、功能边界或优先级变化时。
2. 出现需求变化/重构（新增接口、模块边界变化）时。
3. 里程碑验收后需要回填阶段结论时。

## 验收锚点
1. V2 目标与 `implementation-plan.md` 的 step 定义可一一映射。
2. 对外契约稳定项在迁移期间不退化。
3. 风险项有明确监控与回滚思路。

## 更新时间
2026-02-23

## 1. 阅读导航（先看这里）
1. 先读 `memory-bank/quick-map.md`：确认当前轨道与最小读取顺序。
2. 再读 `memory-bank/implementation-plan.md`：确认 step 门禁与执行顺序。
3. 最后读 `memory-bank/progress.md`：确认当前状态、提交与阻塞信息。

## 2. 背景与问题
V1 已完成可运行基线，但存在三个核心问题：
1. 检索链路手写比例高，重复造轮子，可读性与协作性不足。
2. 架构与进度文档表达不够直观，人类与 AI 上下文切换成本高。
3. 需要兼顾“代码简洁”与“关键边界防护”，避免两个极端。

## 3. V2 目标
1. 采用 LangChain 渐进迁移，优先替换检索编排链路。
2. 文档可读性升级：图内中文注释 + 表格化关键状态 + v3.1 门禁对齐。
3. 保留分层错误体系，确保定位问题时仍可精确归因。
4. 让 AI 与人类都能快速判断“当前该做什么、下一步是什么”。

## 4. 范围与非目标
### 4.1 当前范围（V2 计划）
1. 按 STEP-12~15 渐进推进 LangChain 迁移设计、实现与回归。
2. 维护 `memory-bank` 六文档治理口径一致（状态机、门禁、输出模板）。
3. 保持项目轨道门禁：未收到 `start next step` 不推进下一 step。

### 4.2 非目标（V2 当前阶段）
1. 不改变 `HSIL | LSIL | Uncertain` 判定逻辑与阈值（V2 前半程）。
2. 不新增图像向量检索或服务化主流程入口。
3. 不进行一次性全面代码重写。

## 5. 关键术语（文档协作口径）
1. `AI ReviewCode`：由 AI 对交付物做一致性与质量复核。
2. `提交时间`：仅在 `已提交=✓` 时填写 commit 时间；未提交统一 `-`。
3. `待提交`：功能/文档已完成，但尚未 commit。
4. `blocked`：存在阻塞，必须提供解除条件。
5. `independent_task`：独立任务轨道，`current_step_id` 输出 `N/A` 且不推进项目 step。

## 6. 约束与兼容策略
1. 外部 CLI 输出契约保持兼容：
   - `similar_cases`
   - `tendency`
   - `reason`
   - `disclaimer`
   - `meta`
2. 错误分层策略保留，不退化为模糊异常：
   - `ApiTimeoutError`
   - `ApiAuthError`
   - `ApiRateLimitError`
   - `ApiResponseError`
3. 状态机兼容策略：读取兼容 `in_progress`，写入统一 `ing`。
4. Step 执行遵守门禁：未收到 `start next step` 不进入下一步；跨 step 前需 `/new`。

## 7. 阶段验收标准（V2）
1. `architecture.md` 至少 3 张核心图（当前架构图、时序图、目标架构图）。
2. 三张图中每个脚本节点均包含中文职责注释。
3. `progress.md` 使用 `提交时间`，且未提交步骤统一 `-`。
4. `implementation-plan.md` 与 `progress.md` 的状态/门禁口径一致。
5. `tech-stack.md` 的“现状/目标/保留项”与架构图一致。
6. V2 各 step 完成后可在测试与文档中追溯验收。

## 8. 风险与应对
1. 风险：图注过长导致图拥挤。
   - 应对：图内职责注释保持短句，细节写表格。
2. 风险：提交字段填报不一致。
   - 应对：在 `progress.md` 固化提交时间与 `commit_ref` 填写规则。
3. 风险：文档口径漂移影响执行。
   - 应对：每轮先读 `quick-map.md` 并按 `read_order` 最小读取。

## 9. 当前结论（2026-02-23）
1. 项目轨道 `STEP-13` 已完成并提交（`commit_ref: f14a470`）。
2. 当前焦点为 `STEP-14` 执行中（已收到 `start next step`）。
3. STEP-14 执行环境基线锁定为 conda `vibe-rag`，关键依赖版本见 `tech-stack.md`。
4. only executing current step scope.
