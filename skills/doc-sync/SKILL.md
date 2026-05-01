---
description: Verify and fix documentation accuracy against the actual repo contents. Use when source files change, before committing, or when asked to check docs. Works in any repo by discovering documentation files and cross-referencing against the codebase.
---

# Doc Sync

Verify that all documentation accurately reflects the current state of the repo. Fix any discrepancies found.

## Process

### Step 1: Discover documentation

Find all documentation files in the repo:

```bash
find . -maxdepth 3 -name '*.md' -not -path './.claude/*' -not -path './node_modules/*' -not -path './vendor/*' | sort
```

Key files to always check if they exist: `README.md`, `CLAUDE.md`, `CONTRIBUTING.md`, any files in `docs/` or `doc/`.

### Step 2: Discover what's documentable

Scan the repo for things documentation typically references:

- **Directory structure**: `ls -d */` at the root
- **Entry points**: main files, manifests (`package.json`, `plugin.json`, `go.mod`, `Cargo.toml`, `Makefile`)
- **Agents/skills/hooks**: `agents/*.md`, `skills/*/SKILL.md`, `hooks/`, `.claude/` config files (if a Claude Code plugin)
- **Commands/targets**: `make -qp 2>/dev/null | grep '^[a-zA-Z].*:' | head -30` for Makefile targets
- **Dependencies**: package files, import statements, dependency declarations
- **Config files**: `.env.example`, config templates, env var references

### Step 3: Cross-reference

For each documentation file, check every factual claim against reality:

| Claim type | How to verify |
|-|-|
| File/directory paths mentioned | `ls` or `find` to confirm they exist |
| Commands or CLI examples | `which` or `command -v` for tools; `make -n <target>` for make targets |
| Lists of components (agents, skills, modules, packages) | Compare against actual directory listing |
| Tables cataloguing things | Verify every row exists, verify nothing is missing |
| Diagrams (mermaid, ASCII) | Verify every node/edge corresponds to reality |
| Version numbers | Compare against manifest/config files |
| Default values | Compare against source code |
| Environment variables | Grep source for actual usage |

### Step 4: Report and fix

Report findings as a table:

```
| File | Issue | Fix |
|-|-|-|
| README.md | Agents table missing worktree-worker | Add row |
| CLAUDE.md | Skills list outdated | Update list |
```

If no issues: "All docs are in sync."

If issues found: fix them. Edit the documentation files to match the source of truth. The source of truth is always the code, never the docs.

## Rules

- **Accuracy, not completeness.** Verify what IS documented is correct. Don't flag undocumented features.
- **Code is the source of truth.** When docs and code disagree, the code is right. Fix the docs.
- **Check all doc files, not just one.** The same fact (e.g. list of agents) often appears in multiple files. Update all of them.
- **Diagrams go stale fastest.** Always check mermaid and ASCII diagrams against reality.
- **Read before fixing.** Always read the actual source file before editing docs. Don't fix from memory.

## Plugin-specific checks

When running in a Claude Code plugin repo (detected by `.claude-plugin/` directory):

- Agent catalogue: compare `ls agents/*.md` against any agent tables in docs
- Skill catalogue: compare `ls -d skills/*/` against any skill tables in docs
- Hook catalogue: compare `hooks/hooks.json` entries against any hook tables in docs
- Router dispatch: if `agents/router.md` exists, verify all dispatch targets appear in any dispatch diagrams
- Plugin manifest: verify `version` in docs matches `.claude-plugin/plugin.json`

## Anti-patterns

| Problem | Fix |
|-|-|
| Checking only README.md | Check ALL .md files. CLAUDE.md, docs/, CONTRIBUTING.md. |
| Fixing docs without reading the source | Always read the actual file first. |
| Flagging missing documentation | Only flag inaccuracies. Missing docs is a separate concern. |
| Skipping diagrams | Diagrams go stale fastest. Always check them. |
| Reporting issues without fixing them | If you can fix it, fix it. Don't just report. |
