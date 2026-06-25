---
name: ralph-loop
description: Autonomous Ralph Wiggum Loop — iterative task execution with fresh context, filesystem memory, and git versioning
argument-hint: "[task description or PRD path] [--completion-promise KEYWORD]"
disable-model-invocation: true
---

## Arguments
[task description or PRD path] [--completion-promise KEYWORD]

# Ralph Wiggum Loop

An autonomous coding loop that executes tasks iteratively with **fresh context per iteration**, using the filesystem as memory and `git` for version control. Inspired by the [Ralph Wiggum pattern](https://ghuntley.com/ralph/) — persistent trial-and-error with external state tracking.

## Core Principle

**Ralph loop = Fresh context + Filesystem memory + Git versioning**

Each iteration starts with a clean context window. Progress is tracked in `PROGRESS.md`, requirements live in `PRD.md`, and every completed task is committed to git. This avoids context pollution and produces reliable results for multi-step work.

## Usage

```bash
/ralph-loop "Build the authentication module"
/ralph-loop docs/plans/my-plan.md
/ralph-loop "finish all slash commands" --completion-promise "DONE"
```

## Execution Flow

### Phase 0: Planning (if no PRD exists)

If the argument is a task description (not a path to an existing PRD or plan file):

1. **Read existing plan files** — Check `docs/plans/` for a relevant plan. If one exists and matches the task, use it as the PRD.
2. **Generate PRD** — If no plan exists, create `PRD.md` in the project root with:
   - **Goal**: One-sentence summary of what success looks like
   - **Tasks**: Numbered list of atomic, independently-executable tasks
   - **Acceptance Criteria**: Testable criteria for each task
   - **Completion Promise**: The keyword to output when all tasks are done (default: `DONE`)

3. **Generate PROGRESS.md** — Create `PROGRESS.md` in the project root with:
   ```markdown
   # Progress

   ## Status: IN_PROGRESS

   | # | Task | Status | Notes |
   |---|------|--------|-------|
   | 1 | [task name] | PENDING | |
   | 2 | [task name] | PENDING | |
   ```

4. **Commit initial state**:
   ```bash
   git add PRD.md PROGRESS.md
   git commit -m "ralph-loop: initialize PRD and progress tracking"
   ```

If the argument is a path to a plan file (e.g., `docs/plans/feature.md`), use that as the PRD and generate only `PROGRESS.md` from its tasks.

### Phase 1: Coordination Loop

Read `PRD.md` and `PROGRESS.md` to determine the next PENDING task, then execute iterations until all tasks are complete.

For **each iteration**:

#### Step 1 — Pick Next Task

Read `PROGRESS.md` and select the first task with status `PENDING`. If no PENDING tasks remain, go to Phase 2 (Completion).

#### Step 2 — Execute Task

Spawn a **fresh sub-agent** (via the Task tool) for the selected task. The sub-agent prompt MUST include:

```
You are a Ralph Executor. Complete this single task with fresh context.

**Task:** [task description from PRD]
**Acceptance Criteria:** [criteria from PRD]

Instructions:
1. Read PRD.md and PROGRESS.md for full context
2. Implement the task — write code, create files, run tests
3. Verify your work meets the acceptance criteria
4. Update PROGRESS.md: set this task's status to DONE with brief notes
5. Stage and commit your changes:
   git add -A
   git commit -m "ralph-loop: complete task [N] — [brief description]"

Do NOT modify other tasks. Do NOT skip testing. One task only.
```

<critical_requirement>
Each executor sub-agent runs with **fresh context** — it has no memory of previous iterations. All state comes from the filesystem (PRD.md, PROGRESS.md, existing code, git history).
</critical_requirement>

#### Step 3 — Verify Completion

After the executor sub-agent completes:

1. **Read PROGRESS.md** — Confirm the task status was updated to `DONE`
2. **Quick review** — Spawn a brief reviewer sub-agent to check:
   - Does the code compile/pass linting?
   - Were tests added or do existing tests still pass?
   - Does the change match the acceptance criteria?
3. **If review fails** — Update task status to `FAILED` with notes, then re-attempt. Each task gets up to 3 total attempts (1 initial + 2 retries). After the third failed attempt, mark the task as `BLOCKED` and continue to the next task.
4. **If review passes** — Continue to next iteration (back to Step 1)

### Phase 2: Completion

When all tasks in `PROGRESS.md` are `DONE` (or `BLOCKED`):

1. **Update PROGRESS.md** — Set top-level status:
   - `COMPLETE` if all tasks are DONE
   - `PARTIAL` if any tasks are BLOCKED

2. **Final commit**:
   ```bash
   git add PROGRESS.md
   git commit -m "ralph-loop: all tasks complete"
   ```

3. **Output completion promise** — If `--completion-promise` was provided:
   ```
   <promise>[KEYWORD]</promise>
   ```
   Default keyword is `DONE`.

4. **Summary**:
   ```
   ✓ Ralph Loop Complete

   Tasks: [N] total, [X] done, [Y] blocked
   Commits: [Z] commits made
   PRD: PRD.md
   Progress: PROGRESS.md

   Blocked tasks (if any):
   - Task [N]: [reason]
   ```

## Integration with Compound Engineering

The ralph-loop skill works with existing CE skills:

- **As orchestrator**: Called by `/lfg` and `/slfg` as an optional first step to autonomously execute all workflow commands
- **With `/ce-plan`**: Can use plan files from `docs/plans/` as the PRD input
- **With `/ce-work`**: Each executor iteration is similar to a focused `/ce-work` session
- **With `/ce-review`**: The verification step performs lightweight review; for thorough review use `/ce-review` after the loop completes
- **With `/ce-compound`**: After loop completion, run `/ce-compound` to document learnings

## State Files

| File | Purpose | Created By |
|------|---------|------------|
| `PRD.md` | Requirements and task list | Phase 0 (Planning) |
| `PROGRESS.md` | Task status tracking | Phase 0, updated each iteration |

These files are committed to git and serve as the **filesystem memory** that enables fresh-context execution.

## Design Decisions

- **One task per iteration**: Keeps each sub-agent focused and prevents context pollution
- **Git commits per task**: Enables rollback of individual tasks and provides audit trail
- **3 total attempts per task**: 1 initial attempt + up to 2 retries prevents infinite loops on genuinely broken tasks
- **Reviewer sub-agent**: Catches issues before they compound across iterations
- **BLOCKED status**: Allows the loop to continue past stuck tasks rather than halting entirely

## Common Mistakes to Avoid

| ❌ Wrong | ✅ Correct |
|----------|-----------|
| Execute multiple tasks in one sub-agent | One task per sub-agent with fresh context |
| Skip git commits between tasks | Commit after every completed task |
| Carry conversation context across iterations | Each iteration reads state from filesystem |
| Retry failed tasks indefinitely | 3 total attempts (1 initial + 2 retries), then mark BLOCKED and continue |
| Modify PRD.md during execution | PRD.md is read-only after planning phase |
