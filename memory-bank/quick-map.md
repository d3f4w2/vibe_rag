# Quick Map（会话入口）

## 文档目的
1. 作为 `memory-bank` 第一入口，帮助 AI 与人类在 30-60 秒内定位当前任务与下一动作。
2. 固化最小读取顺序，避免每轮无理由全量扫读。
3. 提供冲突处理、例外审计、输出模板的统一锚点。

## 范围内
1. 当前焦点与任务轨道标注（项目 step / 独立任务）。
2. 标准 `read_order` 与文件索引。
3. 决策锚点、更新触发、快速自检项。

## 范围外
1. 具体业务实现细节与临时代码命令。
2. 测试执行日志与调试过程记录。
3. 对 `progress.md` 以外 step 状态的来源覆盖。

## 真源文档
1. `C:\Users\ljh\Desktop\workflow\工作流v3.1.txt`
2. `memory-bank/progress.md`

## 依赖文档
1. `memory-bank/progress.md`
2. `memory-bank/implementation-plan.md`
3. `memory-bank/prd.md`
4. `memory-bank/architecture.md`
5. `memory-bank/tech-stack.md`

## 更新触发
1. 当前 step 变化（`todo|ing|blocked|待提交|done`）时更新。
2. 会话主任务切换（项目 step <-> 独立任务）时更新。
3. 阅读顺序、规则锚点、必读文件集合发生变化时更新。

## 验收锚点
1. `read_order` 与实际执行顺序一致。
2. 当前焦点可唯一定位项目轨道和独立任务轨道。
3. 冲突模板字段与全局口径一致：`conflict_point/applied_priority/resolution_result`。

## 更新时间
2026-02-23

## 当前焦点
1. 当前项目主线：RAG V2（LangChain 渐进迁移）。
2. 项目轨道当前 step：`STEP-14`（执行中，LangChain 主链路迁移）。
3. 当前独立任务：无（当前会话在项目 step 轨道）。

## read_order（最小读取顺序）
```yaml
read_order:
  - memory-bank/quick-map.md
  - memory-bank/progress.md
  - memory-bank/implementation-plan.md
  - memory-bank/prd.md
  - memory-bank/architecture.md
  - memory-bank/tech-stack.md
```

## 文件索引
| 文件 | 职责 | 何时阅读 |
|---|---|---|
| `memory-bank/quick-map.md` | 会话入口与定位索引 | 每次新会话开始 |
| `memory-bank/progress.md` | 当前 step、状态、提交、阻塞 | 开始执行前与收口后 |
| `memory-bank/implementation-plan.md` | step 清单、门禁与完成标准 | 进入或恢复 step 前 |
| `memory-bank/prd.md` | 需求边界与验收目标 | 任务类型变化时 |
| `memory-bank/architecture.md` | 模块职责、依赖与架构图 | 设计改动或里程碑时 |
| `memory-bank/tech-stack.md` | 技术栈现状与迁移目标 | 选型/重构决策时 |

## 决策记录锚点
1. 规则冲突时输出：
   - `conflict_point`
   - `applied_priority`
   - `resolution_result`
2. 框架例外时补充：
   - `exception_reason`
   - `alternatives_evaluated`
   - `risk_if_no_exception`
   - `rollback_plan`
