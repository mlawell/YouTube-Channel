---
name: atv-update
description: "Update ATV Starter Kit to the latest version. For Copilot CLI marketplace plugins (`atv-skill-*`, `atv-pack-*`, `atv-everything`, `atv-agents`): runs `copilot plugin update` per installed ATV plugin with per-step confirmation. For project scaffold (`atv init`): reports the version delta and prints the exact commands you can run — does NOT auto-rerun the installer because today's installer is additive-only and would not refresh existing files. Triggers on 'atv update', 'update atv', 'upgrade atv', 'atv upgrade', 'refresh atv', 'atv latest'."
argument-hint: "[mode: dry-run | apply (default)]"
---

# /atv-update — Update ATV Starter Kit

Bring your ATV install up to the latest version. Handles both install paths:

- **Marketplace plugins** — auto-updated via `copilot plugin update` (with per-plugin confirmation).
- **Project scaffold** — advisory only. Today's installer is `additive-only` and `npx atv-starterkit@latest init` will NOT refresh existing scaffold files. This skill prints the version delta and the exact commands you can run yourself.

> **Future:** Once the installer gains a `--refresh` flag (read manifest → overwrite checksum-clean files → preserve drifted files), this skill will gain auto-update for project scaffold too. Tracked as a known gap.

## Arguments

<mode> #$ARGUMENTS </mode>

**Mode detection:** Check if arguments contain `dry-run` or `dry` (case-insensitive) → dry-run mode. Otherwise → apply mode (default).

## Execution Flow

```
Phase 1: Detect install scope         → same as /atv-doctor Phase 1
Phase 2: Read installed versions      → manifest (project) + plugin.json files (marketplace)
Phase 3: Fetch latest npm version     → npm view
Phase 4: Show changelog (best-effort) → fetch + parse, fall back to link
Phase 5: Plan update                  → structured table of components + commands
Phase 6: Apply (marketplace only)     → copilot plugin update with confirmation
Phase 7: Verify (suggest /atv-doctor)
```

---

## Phase 1: Detect install scope

Same detection logic as `/atv-doctor` Phase 1 — repo-artifact-based, not manifest-only:

| Flag | Detection |
|------|-----------|
| `hasProject` | any of `.github/skills/`, `.github/copilot-instructions.md`, `.github/copilot-mcp-config.json` exists |
| `hasManifest` | `.atv/install-manifest.json` exists |
| `hasMarketplace` | `~/.copilot/installed-plugins/atv-starter-kit/` exists |

If `!hasProject && !hasMarketplace`: print "No ATV install detected. Nothing to update. Run `npx atv-starterkit init` to scaffold, or `copilot plugin marketplace add All-The-Vibes/ATV-StarterKit` to register the marketplace." and stop.

---

## Phase 2: Read installed versions

### Project (when `hasProject && hasManifest`)

```bash
node -e "console.log(JSON.parse(require('fs').readFileSync('.atv/install-manifest.json','utf8')).catalogVersion || 'unknown')"
```

When `hasProject && !hasManifest`: project version is unknown (auto-mode doesn't write a manifest). Note this and continue — `/atv-update` will still recommend running the installer.

### Marketplace plugins

Walk `~/.copilot/installed-plugins/atv-starter-kit/` directly. For each subdirectory with a `plugin.json`, read `name` and `version`:

```bash
for dir in ~/.copilot/installed-plugins/atv-starter-kit/*/; do
  if [ -f "$dir/plugin.json" ]; then
    node -e "const p = require('$dir/plugin.json'); console.log(p.name + '\t' + (p.version || 'unknown'))"
  fi
done
```

Build a list `{name, currentVersion}` for each ATV plugin.

---

## Phase 3: Fetch latest npm version

```bash
LATEST=$(npm view atv-starterkit version 2>/dev/null)
```

All ATV plugins share the kit's release cadence — the latest plugin version equals the latest npm version. If the call fails: print "Could not reach the npm registry. Skipping update plan." and stop.

---

## Phase 4: Show changelog (best-effort)

Always print the version numbers regardless of network state:

```
ATV Starter Kit
  Latest:   <LATEST>
  Project:  <PROJECT_VERSION or "unknown">
  Plugins:  N installed (mixed versions: <list>)
```

Then attempt to fetch the changelog snippet:

```bash
curl -fsSL https://raw.githubusercontent.com/All-The-Vibes/ATV-StarterKit/main/CHANGELOG.md 2>/dev/null
```

If the fetch succeeds, attempt to extract the section between the heading for the current version and the heading for the latest version (heading format `## [X.Y.Z] — YYYY-MM-DD`). Print up to ~80 lines of that excerpt.

If the fetch or parse fails, just print:

> See https://github.com/All-The-Vibes/ATV-StarterKit/blob/main/CHANGELOG.md for what's new.

This is best-effort — never block the rest of the flow on changelog availability.

---

## Phase 5: Plan update

Build a structured plan and print it. Two sections:

### Project scaffold (advisory only)

If `hasProject` and project version is behind the latest, print:

```
📋 Project scaffold update (manual)

The installer is currently additive-only. `npx atv-starterkit@latest init`
will NOT refresh existing scaffold files. To update your project scaffold,
choose one approach:

Option A — Review and apply selectively (preserves customizations):
  • Visit https://github.com/All-The-Vibes/ATV-StarterKit
  • Diff the templates against your .github/ files
  • Apply changes that matter to you

Option B — Clean reinstall (loses local edits to ATV files):
  npx atv-starterkit@latest uninstall
  npx atv-starterkit@latest init  # or `init --guided`

Option C — Wait for installer refresh support (tracked as a known gap)
```

If `hasProject` but project version equals the latest: print "Project scaffold is up to date." and skip Options.

### Marketplace plugins (auto)

For each plugin from Phase 2 that's behind `LATEST`, list it as:

```
🔄 Marketplace updates available (Phase 6 will run these):
  • copilot plugin update <name>   (current: vX.Y.Z → latest: vA.B.C)
  • ...
```

If all plugins are up to date: print "All marketplace plugins are up to date."

---

## Phase 6: Apply (marketplace only)

**Skip this phase entirely in `dry-run` mode.**

Project scaffold updates are NEVER auto-applied — see Phase 5 rationale.

For each marketplace plugin from Phase 5 that's behind:

1. Use `AskUserQuestion`:
   > Update `<plugin-name>` from v<current> to v<latest> now? (y/n)
2. On `y`: run `copilot plugin update <plugin-name>`. Capture output.
3. On `n`: skip and continue.
4. On error: report the failure clearly and continue with the next plugin.

After the loop, print a summary:

```
Updated N marketplace plugins.
Skipped M.
Errored on X (see above for details).
```

---

## Phase 7: Verify

After applying any changes, suggest:

> Run `/atv-doctor` to verify the post-update install state.

Don't run it automatically — let the user choose.

---

## What this skill does NOT do

- Auto-refresh project scaffold files (installer limitation; tracked as future work).
- Update gstack — that's `gstack`'s own responsibility (gstack syncs from its source repo).
- Update agent-browser — `npm install -g agent-browser` is manual.
- Pin specific versions — `copilot plugin install plugin@marketplace` doesn't accept a version. All ATV plugins share the kit version.
- Roll back to a previous version — `copilot plugin uninstall` then `install` to a specific tag is the manual path.
