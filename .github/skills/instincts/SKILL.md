---
name: instincts
description: Show all learned instincts for this project with confidence scores, grouped by domain. Use to review what the project has learned and identify patterns ready for evolution.
---

# /instincts — View Learned Patterns

Display all instincts learned for this project, grouped by domain with confidence scores.

## Execution Flow

### Step 1: Read Instincts

Read `.atv/instincts/project.yaml`. If the file doesn't exist, report:
```
No instincts found. Run /learn to extract patterns from your work.
```

### Step 2: Display Dashboard

Group instincts by domain and show:

```
Project Instincts — [project name from git remote or directory]

  Code Style (3 instincts)
    ● prefer-early-returns      0.8  "use early returns instead of deep nesting"     12 obs
    ● kebab-case-files          0.7  "name files with kebab-case"                     8 obs
    ○ trailing-commas           0.4  "use trailing commas in multi-line literals"      3 obs

  Error Handling (2 instincts)
    ★ always-wrap-errors        0.9  "wrap errors with fmt.Errorf using %w"          15 obs
    ● sentinel-errors           0.6  "use sentinel errors for expected conditions"    5 obs

  Testing (2 instincts)
    ● table-driven-tests        0.7  "use table-driven test pattern"                  9 obs
    ○ test-helpers-in-helpers   0.3  "put test helpers in _test.go helpers file"      2 obs

  Legend: ★ ready to evolve (>0.8)  ● active  ○ tentative (<0.5)
  Total: 7 instincts across 3 domains
  Last learned: 2026-04-06
```

### Step 3: Recommendations

After the dashboard, suggest actions:

- If any instincts have confidence > 0.8: "★ N instincts are ready to evolve into skills. Run /evolve"
- If no instincts exist: "Run /learn to extract patterns from your recent work"
- If instincts exist but are old (last_seen > 14 days): "Some instincts are stale. Run /learn to refresh"

## Confidence Indicators

| Symbol | Range | Meaning |
|--------|-------|---------|
| ★ | > 0.8 | Ready to evolve into a full skill |
| ● | 0.5–0.8 | Active — seen multiple times |
| ○ | < 0.5 | Tentative — needs more evidence |
