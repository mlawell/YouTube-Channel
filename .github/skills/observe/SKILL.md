---
name: observe
description: Start a focused observation session to analyze specific patterns in the codebase. Watches a domain or file pattern and records findings for future /learn runs.
---

# /observe — Targeted Pattern Analysis

Run a focused observation session on a specific domain, file pattern, or question. Unlike `/learn` which broadly scans recent work, `/observe` lets you zoom in on a specific area.

## When to Use

- When you want to understand how a specific pattern is used across the codebase
- When you suspect an inconsistency and want data
- When onboarding to a new area of the code
- When you want to document "how we do X here"

## Execution Flow

### Step 1: Determine Focus

If the user provides a focus topic, use it. Otherwise ask:
```
What should I observe? Examples:
  - "error handling" — how errors are wrapped, propagated, and reported
  - "test patterns" — how tests are structured and organized
  - "naming conventions" — variable, function, and file naming
  - "src/api/**" — patterns in a specific directory
  - "imports" — how dependencies are organized
```

### Step 2: Gather Evidence

Based on the focus, run targeted analysis:

**For code pattern focus:**
1. Search for relevant code patterns using grep/glob
2. Sample 10-20 representative files
3. Look for consistency and deviations
4. Check git blame for when patterns were established

**For directory focus:**
1. List all files in the target path
2. Analyze file organization and naming
3. Read representative files for patterns
4. Check for README or documentation

**For workflow focus:**
1. Read `.atv/observations.jsonl` for relevant tool use
2. Check git log for commit patterns
3. Look at CI/CD configuration
4. Check for scripts or Makefiles

### Step 3: Analyze Findings

For each observation, evaluate:

| Question | Why |
|----------|-----|
| Is this pattern consistent? | Consistency = high confidence instinct |
| How many files follow it? | Volume = evidence strength |
| Are there deviations? | Deviations = either evolution or mistakes |
| When was it established? | Age = stability indicator |
| Is it documented anywhere? | Documentation = intentional choice |

### Step 4: Record Results

Append findings to `.atv/observations.jsonl` with a special observation type:

```json
{
  "ts": "2026-04-06T10:30:00Z",
  "hook": "manual-observe",
  "focus": "error handling",
  "findings": [
    "All errors wrapped with fmt.Errorf %w in 18/20 files",
    "Two files use bare error returns (legacy code from 2024)",
    "Custom error types in pkg/errors/ for domain errors",
    "No panic() usage found — errors always returned"
  ],
  "suggested_instincts": [
    {
      "id": "always-wrap-errors",
      "trigger": "when returning an error from a function",
      "behavior": "wrap with fmt.Errorf using %w verb"
    }
  ]
}
```

### Step 5: Report

```
Observation: [focus topic]

Findings:
  1. [Pattern] — found in N/M files examined (X% consistent)
  2. [Pattern] — found in N/M files examined (X% consistent)
  3. [Deviation] — N files deviate from the dominant pattern

Suggested instincts (run /learn to formalize):
  + [instinct-id] — "[behavior]" (evidence: N files)
  + [instinct-id] — "[behavior]" (evidence: N files)

Existing instincts affected:
  ↑ [instinct-id] — additional evidence found (+N observations)
  ? [instinct-id] — contradictory evidence found (N deviations)

Next steps:
  - Run /learn to incorporate these findings into instincts
  - Run /observe "[related topic]" to dig deeper
  - Review deviations — they may be intentional or need fixing
```

## Quick Observations

For rapid pattern checks without full analysis:

```
/observe --quick "how do we handle auth?"
```

Quick mode:
1. Searches for relevant files (auth, middleware, session, token)
2. Reads the most relevant 3-5 files
3. Summarizes the pattern in 3-5 bullet points
4. Does NOT write to observations.jsonl

## Notes

- Observations are raw data — run `/learn` to turn them into instincts
- Manual observations have higher signal than automatic hook observations
- The `manual-observe` hook type in observations.jsonl lets `/learn` weight these higher
- Observations are additive — run multiple times on different topics
