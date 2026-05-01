# clawdio

Personal Claude Code plugin for SDLC automation.

## Architecture

Router agent dispatches to specialist subagents based on the task. Skills provide cross-cutting knowledge. Hooks enforce guardrails.

```
you -> router -> specialist subagent(s) -> result
                    |
                    +-- skills (what-next, ship, pr-description, issues, doc-sync)
                    +-- hooks (block secrets, doc-sync-reminder, lint, format)
```

## Structure

```
agents/          subagent definitions (.md)
skills/          on-demand skills (SKILL.md per directory)
hooks/           lifecycle hooks (hooks.json)
references/      supporting docs agents can read
docs/            architecture, contributing, project context
.claude-plugin/  plugin manifest and marketplace config
```

## Key files

| File | Purpose |
|-|-|
| `agents/router.md` | Task intake and dispatch to specialist agents |
| `agents/worktree-worker.md` | Isolated implement-to-PR agent for parallel issue work |
| `skills/ship/SKILL.md` | End-to-end issue-to-merged-PR lifecycle |
| `skills/doc-sync/SKILL.md` | Cross-references docs against repo contents, fixes drift |
| `hooks/hooks.json` | Lifecycle hooks -- secret blocking, doc-sync reminders |
| `.claude-plugin/plugin.json` | Plugin manifest: name, version, dependencies |

## Keeping docs in sync

After any change to `agents/`, `skills/`, or `hooks/`, invoke `clawdio:doc-sync` before committing. It verifies README.md, CLAUDE.md, docs/architecture.md, and docs/contributing.md against the actual repo contents and fixes discrepancies.

## Conventions

- Agents: as short as possible. Decision trees, anti-pattern tables, verification checklists where they earn their place.
- Skills: progressive disclosure. Lead with the rule, details below.
- Hooks: deterministic, fast, fail silently if tools missing.
- British English in all user-facing text.
- No emojis. No AI-sounding prose.

## Dependencies

- [agent-skills](https://github.com/addyosmani/agent-skills) plugin for security, code review, TDD, debugging, git workflow
- [dev-team-plugin](https://github.com/kuadrant/dev-team-plugin) plugin for design docs, feature lifecycle, Go PR review
- `gh` CLI (authenticated) for GitHub operations
- GitHub MCP server for issue/PR comment threads
- [Atlassian MCP](https://github.com/sooperset/mcp-atlassian) for Jira integration (optional)

## Docs

- [docs/architecture.md](docs/architecture.md) -- design rationale and decisions
- [docs/contributing.md](docs/contributing.md) -- how to write agents, skills, hooks
- [docs/references.md](docs/references.md) -- Claude Code primitives and execution surfaces
