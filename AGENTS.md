# Workflow Rules (Initialized from `memory-bank/prd.md` + `memory-bank/tech-stack.md`)

## 1) Rule Priority (Conflict Resolution)
1. `Always rules` > `Execution flow description` > `Example statements`.
2. If conflicts exist, execute by the priority above and explicitly output:
   - Conflict point
   - Resolution result

## 2) Key Terms
1. Small change: must satisfy all conditions:
   - Does not modify acceptance criteria in `memory-bank/prd.md`.
   - Does not add/modify public interfaces (API, CLI, external I/O contracts).
   - Does not change core directory structure or module boundaries.
2. Requirement change/refactor: if any condition is met:
   - Modifies acceptance criteria or feature boundaries in `memory-bank/prd.md`.
   - Adds/modifies public interfaces (API, CLI, external I/O contracts).
   - Adjusts core directory structure, module boundaries, or key dependencies.
3. Major feature: new user-visible capability or new main workflow entry.
4. Milestone:
   - If `epic_id` exists in `memory-bank/implementation-plan.md`, all steps under same `epic_id` are done.
   - If `epic_id` is not used, milestone equals 3 consecutive completed steps.

## 3) Always Rules (Trigger -> Action -> Output)
1. Trigger: before writing any code.
   - Action: read `memory-bank/architecture.md`, `memory-bank/prd.md`, `memory-bank/implementation-plan.md`, `memory-bank/tech-stack.md`, `memory-bank/progress.md`.
   - Output: `read_files + current_step_goal + test_plan_this_round`.
2. Trigger: required reading files are missing.
   - Action: create minimal templates for missing files first, then continue.
   - Output: `missing_files + created_template_files`.
3. Trigger: session starts or execution resumes.
   - Action: choose a unique current step from `memory-bank/progress.md`: prefer `in_progress`; otherwise the `todo` with smallest `step_order`.
   - Output: `current_step_id + selection_reason`.
4. Trigger: one step in `memory-bank/progress.md` is completed.
   - Action: update `memory-bank/progress.md`.
   - Output: step status, test result, manual verification result, change summary.
5. Trigger: after adding a major feature or completing a milestone.
   - Action: update `memory-bank/architecture.md`.
   - Output: module responsibilities, file roles, dependency changes, reason for change.
6. Trigger: human requests new requirement/add/remove feature/refactor.
   - Action: read `memory-bank/` docs and evaluate required sync changes.
   - Output: `docs_to_update + patch_suggestions`.
7. Trigger: rules may not fit current project.
   - Action: ask human for confirmation before changing rules.
   - Output: `proposed_rule_change + reason + impact_scope`.
8. Trigger: task is identified as a small change.
   - Action: still read the 5 Always files first; then focus analysis on `memory-bank/progress.md`, `memory-bank/implementation-plan.md`, `memory-bank/architecture.md`.
   - Output: `small_change_evidence + follow_small_change_flow`.
9. Trigger: task is identified as requirement change/refactor.
   - Action: read full `memory-bank/*`.
   - Output: `refactor_evidence + docs_need_sync`.
10. Trigger: current step has not received human command `start next step`.
    - Action: do not enter next step.
    - Output: explicitly stay in current step and wait for human confirmation.
11. Trigger: AI can see later-step content.
    - Action: do not implement ahead across steps.
    - Output: explicitly state "only executing current step scope".
12. Trigger: blocker occurs (test failure cannot pass, missing dependency, requirement conflict, permission limit, etc.).
    - Action: stop immediately, mark current step as `blocked`, and record unblock conditions.
    - Output: `blocker_description + impact_scope + unblock_conditions + suggested_decision`.
13. Trigger: human completed GitHub commit.
    - Action: backfill `commit_ref` in `memory-bank/progress.md`.
    - Output: `commit_ref_linked`.
14. Trigger: blocker is removed and confirmed by human.
    - Action: move current step status from `blocked` to `in_progress`, update `notes` and `updated_at`.
    - Output: `resume_basis + next_action_after_resume`.

## 4) Mandatory Output Schema per Execution Round
- `current_step_id`
- `goal`
- `tests_failed_summary`
- `tests_passed_summary`
- `manual_test_plan`
- `next_action`
- `blockers` (if any)

## 5) Conflict Reporting Template
When rule conflicts occur, output this explicit structure:
1. `conflict_point`: what conflicts with what.
2. `applied_priority`: which level won (`Always` / `Execution flow` / `Example statement`).
3. `resolution_result`: what was executed and what was deferred or rejected.
