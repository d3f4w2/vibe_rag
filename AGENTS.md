# 工作流规则（基于 `memory-bank/prd.md` + `memory-bank/tech-stack.md` 初始化）

## 1) 规则优先级（冲突裁决）
1. `Always rules` > `Execution flow description` > `Example statements`。
2. 若存在冲突，必须按上述优先级执行，并显式输出：
   - 冲突点（Conflict point）
   - 处理结果（Resolution result）

## 2) 关键术语（Key Terms）
1. Small change（小改动）：需同时满足以下条件：
   - 不修改 `memory-bank/prd.md` 中的验收标准。
   - 不新增或修改公共接口（API、CLI、外部 I/O 契约）。
   - 不改变核心目录结构或模块边界。
2. Requirement change/refactor（需求变化/重构）：满足任一条件即成立：
   - 修改 `memory-bank/prd.md` 的验收标准或功能边界。
   - 新增或修改公共接口（API、CLI、外部 I/O 契约）。
   - 调整核心目录结构、模块边界或关键依赖关系。
3. Major feature（主要功能）：新增用户可感知能力，或新增主流程入口。
4. Milestone（里程碑）：
   - 若 `memory-bank/implementation-plan.md` 使用 `epic_id`，同一 `epic_id` 下全部步骤完成即达成。
   - 若未使用 `epic_id`，连续完成 3 个 step 即视为里程碑。

## 3) Always Rules（Trigger -> Action -> Output）
1. Trigger：在编写任何代码前。
   - Action：读取 `memory-bank/architecture.md`、`memory-bank/prd.md`、`memory-bank/implementation-plan.md`、`memory-bank/tech-stack.md`、`memory-bank/progress.md`。
   - Output：`read_files + current_step_goal + test_plan_this_round`。
2. Trigger：必读文件缺失。
   - Action：先创建缺失文件的最小模板，再继续流程。
   - Output：`missing_files + created_template_files`。
3. Trigger：会话开始或执行恢复。
   - Action：从 `memory-bank/progress.md` 选择唯一当前 step：优先 `in_progress`，否则选择 `step_order` 最小的 `todo`。
   - Output：`current_step_id + selection_reason`。
4. Trigger：`memory-bank/progress.md` 中任一步骤完成。
   - Action：更新 `memory-bank/progress.md`。
   - Output：step 状态、测试结果、人工验证结果、变更摘要。
5. Trigger：新增主要功能或完成里程碑后。
   - Action：更新 `memory-bank/architecture.md`。
   - Output：模块职责、文件角色、依赖变化、变更原因。
6. Trigger：人类提出新增需求/增删功能/重构。
   - Action：读取 `memory-bank/` 文档并评估同步修改需求。
   - Output：`docs_to_update + patch_suggestions`。
7. Trigger：规则可能不适配当前项目。
   - Action：修改规则前先向人类确认。
   - Output：`proposed_rule_change + reason + impact_scope`。
8. Trigger：任务被识别为小改动。
   - Action：仍需先读取 5 个 Always 文件，再重点分析 `memory-bank/progress.md`、`memory-bank/implementation-plan.md`、`memory-bank/architecture.md`。
   - Output：`small_change_evidence + follow_small_change_flow`。
9. Trigger：任务被识别为需求变化/重构。
   - Action：全量读取 `memory-bank/*`。
   - Output：`refactor_evidence + docs_need_sync`。
10. Trigger：当前 step 未收到人类命令 `start next step`。
    - Action：不得进入下一 step。
    - Output：明确停留当前 step 并等待人类确认。
11. Trigger：AI 可见后续步骤内容。
    - Action：不得跨 step 提前实现。
    - Output：明确说明 "only executing current step scope"。
12. Trigger：出现 blocker（如测试无法通过、依赖缺失、需求冲突、权限限制等）。
    - Action：立即停止推进，将当前 step 标记为 `blocked`，并记录解除条件。
    - Output：`blocker_description + impact_scope + unblock_conditions + suggested_decision`。
13. Trigger：人类完成 GitHub commit。
    - Action：回填 `memory-bank/progress.md` 中的 `commit_ref`。
    - Output：`commit_ref_linked`。
14. Trigger：blocker 解除并经人类确认。
    - Action：将当前 step 从 `blocked` 改为 `in_progress`，并更新 `notes` 与 `updated_at`。
    - Output：`resume_basis + next_action_after_resume`。

## 4) 每轮执行的强制输出结构（Mandatory Output Schema）
- `current_step_id`
- `goal`
- `tests_failed_summary`
- `tests_passed_summary`
- `manual_test_plan`
- `next_action`
- `blockers`（如有）

## 5) 冲突报告模板（Conflict Reporting Template）
当发生规则冲突时，必须输出以下结构：
1. `conflict_point`：冲突点是什么。
2. `applied_priority`：采用了哪一层优先级（`Always` / `Execution flow` / `Example statement`）。
3. `resolution_result`：实际执行内容，以及被延后或拒绝的内容。
