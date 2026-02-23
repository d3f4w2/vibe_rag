# Progress Tracker（v3.1）

## 文档目的
1. 维护项目 step 的唯一当前状态与推进轨迹。
2. 固化状态机、门禁、提交回填和 blocker 生命周期。
3. 为会话开始时的 `current_step_id` 选择提供唯一依据。

## 范围内
1. 项目轨道 step 状态总表与状态迁移规则。
2. 当前 step 选择规则、门禁说明、提交与阻塞记录。
3. 与 `implementation-plan.md` 同步的 step 元数据（ID、顺序、目标状态）。

## 范围外
1. 架构设计细节、技术选型论证、长篇执行日志。
2. 与独立任务轨道直接相关的细节过程记录。
3. 非项目 step 的任务看板管理。

## 真源文档
1. `C:\Users\ljh\Desktop\workflow\工作流v3.1.txt`

## 依赖文档
1. `memory-bank/quick-map.md`
2. `memory-bank/implementation-plan.md`
3. `memory-bank/prd.md`

## 更新触发
1. step 状态迁移（`todo -> ing -> 待提交 -> done` 或 `ing <-> blocked`）。
2. 人类完成 commit 后回填 `commit_ref` 或提交时间。
3. blocker 出现/解除。

## 验收锚点
1. 当前 step 可由本文件唯一推导（优先 `ing`，否则最小 `todo`）。
2. 写入口径只使用 `todo|ing|blocked|待提交|done`。
3. 提交字段遵循规则：`已提交=✓` 才有提交时间与 `commit_ref`。

## 更新时间
2026-02-23

## 1. 状态与兼容规则
1. 写入状态枚举固定为：`todo` / `ing` / `blocked` / `待提交` / `done`。
2. 迁移兼容：读取时若出现旧状态 `in_progress`，按 `ing` 处理；写入时不再新增 `in_progress`。
3. 未收到人类命令 `start next step` 前，不得进入下一 step。
4. `阻塞` 默认 `✗`，仅出现 blocker 时置为 `✓`，并在备注写明解除条件。
5. `已提交` 默认 `✗`，仅在人类确认完成 commit 后改为 `✓`。
6. `提交时间` 只记录 commit 时间：
   - `已提交=✓`：填写 commit 时间（ISO 或 `YYYY-MM-DD HH:mm`）。
   - `已提交=✗`：统一填写 `-`。

## 2. 当前执行步选择规则
1. 优先选择 `ing` 状态作为当前 step。
2. 若无 `ing`，选择 `todo` 中 `step_order` 最小的步骤。
3. 禁止跳步，除非人类明确确认规则变更。
4. 若存在 `待提交` 项，当前会话应优先收口，但不改变“当前 step 选择规则”的定义。
5. 独立任务模式下输出 `current_step_id: N/A（独立任务轨道）`，不修改本表 step 状态。

## 3. 当前执行上下文
1. 项目轨道当前 step：`STEP-12`（ing，已收到 `start next step`）。
2. 独立任务轨道：无（当前会话在项目 step 轨道）。

## 4. Step 状态总表
| 步骤ID | step_order | 步骤名称 | 状态 | 自动化测试 | AI ReviewCode | 已提交 | 提交时间 | commit_ref | 阻塞 | 备注 |
|---|---:|---|---|---|---|---|---|---|---|---|
| STEP-01 | 1 | 定义病例元数据结构与输入输出契约 | done | ✓ | ✓ | ✓ | 2026-02-21T15:37:18+08:00 | - | ✗ | V1 基线完成 |
| STEP-02 | 2 | 实现数据目录扫描与完整性校验 | done | ✓ | ✓ | ✓ | 2026-02-21T17:14:45+08:00 | - | ✗ | V1 基线完成 |
| STEP-03 | 3 | 实现 UTF-8 与 0x7F 文本清洗 | done | ✓ | ✓ | ✓ | 2026-02-21T21:07:04+08:00 | - | ✗ | V1 基线完成 |
| STEP-04 | 4 | 解析 PDF 报告时间并写入 JSONL 元数据 | done | ✓ | ✓ | ✓ | 2026-02-21T21:56:21+08:00 | - | ✗ | V1 基线完成 |
| STEP-05 | 5 | 构建检索文档对象 | done | ✓ | ✓ | ✓ | 2026-02-22T13:27:58+08:00 | - | ✗ | V1 基线完成 |
| STEP-06 | 6 | 实现 vector-only 检索链路 | done | ✓ | ✓ | ✓ | 2026-02-22T14:47:42+08:00 | - | ✗ | V1 基线完成 |
| STEP-07 | 7 | 实现倾向判定与解释 | done | ✓ | ✓ | ✓ | 2026-02-22T15:25:11+08:00 | - | ✗ | V1 基线完成 |
| STEP-08 | 8 | 提供 CLI 与结构化 JSON 输出 | done | ✓ | ✓ | ✓ | 2026-02-22T15:41:13+08:00 | - | ✗ | V1 基线完成 |
| STEP-09 | 9 | 完成 V1 回归与失败路径覆盖 | done | ✓ | ✓ | ✓ | 2026-02-22T16:04:12+08:00 | - | ✗ | V1 基线完成 |
| STEP-10 | 10 | 中文友好与新手友好文档同步 | done | ✗ | ✓ | ✓ | 2026-02-22T16:35:28+08:00 | - | ✗ | docs-only |
| STEP-11 | 11 | V2 文档重构（图注增强 + 进度提交时间制） | done | ✗ | ✓ | ✓ | 2026-02-23T09:14:36+08:00 | c44e8e7 | ✗ | 已提交收口；only executing current step scope |
| STEP-12 | 12 | LangChain 迁移设计冻结 | ing | ✓ | ✓ | ✗ | - | - | ✗ | 已完成设计规格冻结与一致性校验，待人工确认后进入待提交；only executing current step scope |
| STEP-13 | 13 | 边界条件精简与测试矩阵重构 | todo | ✗ | ✗ | ✗ | - | - | ✗ | 待人类命令 `start next step` |
| STEP-14 | 14 | 检索主链路渐进迁移到 LangChain | todo | ✗ | ✗ | ✗ | - | - | ✗ | 待人类命令 `start next step` |
| STEP-15 | 15 | V2 回归验收与文档收口 | todo | ✗ | ✗ | ✗ | - | - | ✗ | 待人类命令 `start next step` |

## 5. 阻塞记录（仅有 blocker 时新增）
当前无 blocker。
