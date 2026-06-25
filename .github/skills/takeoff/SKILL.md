---
name: takeoff
description: Start a session with a prioritized backlog briefing. Use when the user says "takeoff", "take off", "/takeoff", "starting a new session", "what should I work on", "kickoff", "what's next", or wants a prioritized view of the backlog at the start of work. Surfaces the top-priority actionable tasks as bullet groups with status, dependencies, and blockers pulled from Backlog.md when available, or falls back to active plans under `docs/plans/`.
---

# Take Off

The session kickoff counterpart to `/land`. Where `/land` closes out work, `/takeoff` *starts* work by giving a crisp, prioritized picture of what to pick up.

## Trigger

Any variation of:
- `/takeoff`, `takeoff`, `take off`, `let's take off`, `time to take off`, `ready to take off`
- `what should I work on`, `what's next`, `kickoff`, `start a new session`, `show me the backlog`

When in doubt and the user is at the *start* of work (not finishing), invoke this protocol.

## What this skill produces

A short, scannable briefing with four sections:

1. **Top Priority** — the N highest-priority actionable tasks
2. **Blocked / Dependent** — tasks that exist but cannot be started
3. **In Progress** — tasks already underway (not to be double-claimed)
4. **Recommendation** — one sentence: "Start with `X` because …"

Keep it terse. The user wants to pick a task and go, not read a report.

## Execution

### Step 1: Verify backlog tooling is present

Check that the current repo has a `backlog/` directory. If not, fall back to reading plan files in `docs/plans/` and summarizing those instead (Step 2b).

```bash
test -d backlog && echo "backlog present" || echo "no backlog — will fall back to docs/plans/"
```

### Step 2: Pull the backlog (preferred path)

Shell out to the backlog CLI only when both the CLI and `backlog/` directory are present. Otherwise fall through to Step 2b:

```bash
if command -v backlog >/dev/null 2>&1 && [ -d backlog ]; then
  backlog task list --plain --sort priority
  backlog sequence list --plain
fi
```

Parse both outputs. Extract: id, title, priority, status, assignee, dependencies, blocked-by.

If the `backlog` CLI is absent but the `backlog/` directory is present, read the task markdown files directly and parse frontmatter for the same fields.

### Step 2b: Fallback — read `docs/plans/`

When no `backlog/` directory exists (the default in ATV-starterkit today), scan `docs/plans/` for plans with `status: active` in the YAML frontmatter:

```bash
for plan in docs/plans/*.md; do
  [ -f "$plan" ] || continue
  # Only consider plans whose frontmatter has `status: active`.
  # awk pulls the first YAML block; grep checks for the active marker.
  if awk '/^---$/{c++; next} c==1' "$plan" | grep -qE '^status:[[:space:]]*active$'; then
    title=$(awk '/^---$/{c++; next} c==1' "$plan" | grep -E '^title:' | sed 's/^title:[[:space:]]*//; s/^"//; s/"$//')
    echo "- $(basename "$plan") — ${title:-(untitled)}"
  fi
done
```

Skip plans with `status: done`, `status: archived`, or missing frontmatter. Mention explicitly in the output that this is a `docs/plans/` fallback because the repo has no `backlog/` directory. If the fallback also yields zero active plans, drop into the empty-list edge case (congratulate + suggest `/ce-ideate` or `/ce-plan`).

### Step 3: Classify each task

For every task returned, bucket it:

| Bucket | Criteria |
|---|---|
| **Actionable** | status = "To Do", no unresolved dependencies, not assigned to someone else |
| **Blocked** | status = "To Do" but has a `blocked_by` / unresolved dependency |
| **In Progress** | status = "In Progress" or "Doing" |
| **Done** | status = "Done" — skip, don't surface |

If a task has a dependency, note *which* task blocks it by ID.

### Step 4: Render as bulleted groups

Sort actionable tasks by priority (HIGH → MEDIUM → LOW), then by ID. By default show the top 5 in the top-priority group. If the user passed `--top N`, honor that. If they passed `--mine`, filter to their assignee.

**Format: flat bullet lists grouped by category, with an emoji header on each secondary group.** Tables wrap poorly in narrow terminals. A plain `- ID — Title` bullet reads cleanly at any width.

Use `—` (em-dash) as the separator between ID and title. For tasks with dependencies, append `(blocked by X, Y)` or `(depends on X)` at the end of the line.

Group headers use these emojis:
- 🛫 Top-priority actionable group (the main recommendation pool)
- 🔵 Epic subtasks, or clusters of related follow-ups
- 🟢 In Progress
- ⚪ LOW / Housekeeping
- 🔴 Blocked / Dependent (only when all blockers are hard blockers)

Emit the output directly as markdown in your final response — no code fences, no custom rendering scripts.

**Shape:**

```markdown
## 🛫 Takeoff — <repo-name>

### Top Priority (actionable)

- AGENTSAPI-1 — Orchestrator admin-agents client + manifest types
- AGENTSAPI-2 — Admin Agents list page + row actions (depends on AGENTSAPI-1)
- NEBULA-42 — PR comment three-step enforcement hook

🔵 DOCREVIEW epic subtasks (children of DOCREVIEW-1)

- DOCREVIEW-1.1 — strip Recommendations strip from final chain message
- DOCREVIEW-1.2 — generalize Review Document button via ChainConfig

🟢 In Progress

- AGENTSAPI-7 — something currently being worked on (@sam)

⚪ LOW / Housekeeping

- NEBULA-35 — Enforce backlog.md usage via MCP server and hooks

### Recommendation
Start with **AGENTSAPI-1**. It's the next unblocked HIGH-priority item and clears the path for 2 more.
```

**Formatting rules:**
- One task per line. Do not wrap a task across multiple lines.
- Group headers use H3 (`###`) for top-priority only; secondary groups use a bold-emoji line (e.g., `🔵 DOCREVIEW epic subtasks`), not an H-level heading.
- Omit groups that have zero tasks. If In Progress is empty, skip the section.
- Never emit a table. No pipes, no box-drawing characters.
- Do not truncate titles; rely on bullets to wrap cleanly at any width.

### Step 5: Offer a next step

End with a single question: "Want me to open the plan for `<ID>` and start `/ce-work` on it?" — do not auto-start. Takeoff is for orientation, not execution.

### Step 6: Final banner

After the recommendation question, emit a single final line:

```
✈️ TAKE OFF — NOW AT 30,000 FEET
```

This **must** be the last line of output — no content after it, no code fence, no trailing heading. It fires on every successful completion path, including the no-backlog fallback and the empty-task-list edge case. Do not emit the banner if the routine aborts before producing a briefing.

## Formatting rules

- **Bullets, not tables.** Tables break at narrow widths; bullets flow cleanly.
- **Group with emoji headers.** 🛫 top-priority, 🔵 related clusters / epics, 🟢 in progress, ⚪ housekeeping, 🔴 hard-blocked.
- **Never hide blockers.** Annotate dependencies inline with `(blocked by X)` — don't silently drop the task.
- **Show dependency IDs explicitly.** `(blocked by AGENTSAPI-1)` is useful; `(has dependencies)` is not.
- **Be honest about emptiness.** If there are zero actionable tasks, say so and suggest creating one or picking up in-progress work.
- **Always end with the takeoff banner.** The final line of every successful invocation must be `✈️ TAKE OFF — NOW AT 30,000 FEET`.

## Why this shape

Takeoff's job is one concentrated briefing that answers *"what am I about to do and why"* in under 15 seconds of reading. Bullets + a one-line recommendation beat a paragraph because the user is scanning, not reading.

Dependencies matter more than priority on their own — a HIGH task that's blocked is worse than a MEDIUM task that's ready. The recommendation should factor in unblocking power, not just raw priority.

## Arguments

- `--top N` — show N tasks in the top-priority group (default 5)
- `--mine` — filter to tasks assigned to the current user (resolve via `git config user.email` or `git config user.name`)
- `--all` — also include LOW priority actionable tasks
- `--tag <tag>` — filter by a backlog tag/label

If no arguments are given, use defaults.

## Edge cases

- **No `backlog/` directory** → fall back to `docs/plans/` summaries (Step 2b); tell the user.
- **`backlog/` present but CLI missing** → parse task markdown files directly.
- **`backlog` CLI returns non-zero** → report the error honestly, fall back to `docs/plans/`, still emit banner.
- **Everything is blocked** → surface the root blockers and ask whether to create a task to unblock them.
- **Task list is empty** → congratulate the user and suggest `/ce-ideate` or `/ce-plan` to generate new work.
- **Tasks without priority set** → treat as MEDIUM.
