# Architecture

## Origin

This plugin replaces clawdio, a custom Go orchestrator for managing AI agent sessions. After a structured interview (April 2025), the conclusion was: the orchestrator was over-built. The bottleneck was never orchestration infrastructure -- it was agent reliability. The investment should go into building good agents, skills, and hooks that work natively in Claude Code.

## Design decisions

### Why a plugin, not an orchestrator

Clawdio provided: work item database, GitHub polling, worktree management, tmux session lifecycle, skill-based prompt construction, workflow chaining (implement > review > merge), and a TUI for monitoring agents.

Most of this is now covered by Claude Code natively:
- Git worktrees: EnterWorktree/ExitWorktree tools
- GitHub operations: `gh` CLI or GitHub MCP server
- Skills: `.claude/skills/*.md`, loaded on demand
- Subagents: `.claude/agents/*.md`, isolated context windows
- Hooks: pre/post tool use, deterministic shell commands
- Session resume: `--resume` flag

What clawdio added on top was multi-agent spawning, monitoring, and workflow chaining. But the user works serially in practice, and the fanout pattern (router agent dispatching specialists) handles workflow chaining in natural language rather than hardcoded YAML transitions.

### Router + specialist pattern

A single router agent (router.md) serves as the entry point for all tasks. It:
1. Assesses what the user needs
2. Picks the right specialist subagent(s)
3. Dispatches them (possibly in parallel for multi-pass review)
4. Collects results and reports back

This replaces clawdio's workflow engine. The routing logic is in natural language, making it flexible for edge cases that YAML transitions couldn't handle.

### Multi-pass review

Reviews use the fanout pattern: the router classifies the PR's file paths, then spawns multiple specialist reviewers in parallel. A Go/K8s PR gets the Go/K8s specialist. An auth/policy PR gets the auth/policy specialist. Security-sensitive changes get a security auditor. A test-verifier always runs to check the test plan. Results are collected and presented grouped by specialist.

The router owns this fanout directly because subagents cannot spawn sub-subagents (they don't have access to the Agent tool). There is no intermediate "review coordinator" agent.

### Three-tier primitive location

1. **Per-repo** (`.claude/` in each project): CLAUDE.md, repo-specific agents and hooks
2. **Personal plugin** (this repo, installed to `~/.claude/plugins/`): cross-cutting SDLC agents, shared skills, workflow preferences
3. **Org-level** (future): shared plugin for team use

### Vertex auth

All work uses Google Vertex AI for Claude access (work account). No direct Anthropic API access currently. This doesn't constrain the architecture -- Claude Code, GitHub Actions (claude-code-action), and the Agent SDK all support Vertex via environment variables.

### Future: Agent SDK

Start with Claude Code (interactive). When the ceiling is hit (need scheduling, GHA integration, custom UIs, Backstage plugin), port the agents to the Agent SDK. The skills and agent definitions translate directly.

## Success metric

"I open Claude, say 'what's on?', it shows my priorities, I tell it to go."

## User profile

- Senior software engineer
- Works across 3-5 repos in a typical week
- Mix of feature implementation, PR review, and bug investigation
- Deliberate process: read > refine > plan > code > self-review > PR > team review > feedback > merge
- Uses AI assistance across multiple steps, not just for coding
- Team is actively adopting AI workflows
- For personal repos: full autonomy, autopilot acceptable
- For team repos: agents assist, but human stays in the loop

## Agent catalogue

| Agent | Purpose | Scope |
|-|-|-|
| router | Task intake, classification, delegation, review coordination | Plugin |
| implement | Takes a well-defined issue, writes code, runs tests, commits | Plugin |
| code-reviewer | General code quality review | Plugin |
| security-auditor | Security-focused review (OWASP, injection, secrets) | Plugin |
| go-k8s-reviewer | Go/Kubernetes specialist reviewer (generic; override in ~/.claude/agents/) | Plugin |
| auth-reviewer | Auth/policy specialist reviewer (generic; override in ~/.claude/agents/) | Plugin |
| triage | Assesses new issues, labels, prioritises, checks readiness | Plugin |
| refine | Takes vague issues, asks clarifying questions, produces acceptance criteria | Plugin |
| address-feedback | Takes review comments on a PR, fixes them | Plugin |
| release-notes | Generates release notes between tags | Plugin |
| test-writer | Writes tests, finds coverage gaps | Plugin |
| test-verifier | Verifies PR test plans, runs tests, drives browser for UI checks | Plugin |
| docs | Documentation writing and updating | Plugin |

Note: subagents cannot spawn sub-subagents (no access to the Agent tool). The router owns all agent dispatch, including review fanout to specialist reviewers in parallel.

## Skill catalogue

| Skill | Purpose |
|-|-|
| what-next | Scans GitHub for actionable work, suggests priorities |
| ship | Full lifecycle: implement > push > PR > review > merge |
| pr-description | PR body template and conventions |

Skills for commit conventions, security checklists, and review rubrics are provided by the companion plugin [agent-skills](https://github.com/addyosmani/agent-skills) (`git-workflow-and-versioning`, `security-and-hardening`, `code-review-and-quality`).

## Hook catalogue

| Hook | Trigger | Purpose |
|-|-|-|
| lint-on-edit | PostToolUse (Write/Edit) | Run linter after every file edit |
| block-env-writes | PreToolUse (Write/Edit) | Prevent writing to .env, credentials files |
| format-on-save | PostToolUse (Write/Edit) | Auto-format code after edits |

## MCP servers

| Server | Purpose |
|-|-|
| GitHub MCP | Issues, PRs, Actions, releases, code search |

## Dependencies

| Dependency | Type | Purpose |
|-|-|-|
| [agent-skills](https://github.com/addyosmani/agent-skills) | Claude Code plugin | Companion skills (security, code review, TDD, debugging, git workflow) |
| `gh` CLI | CLI tool | GitHub issue/PR operations (must be authenticated) |
| GitHub MCP server | MCP server | Issue/PR comments, review threads |

## References

- [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) -- companion plugin, installed alongside workbench
- Claude Code plugin format: `.claude-plugin/plugin.json` manifest, `agents/`, `skills/`, `hooks/` directories
- Clawdio v2 vision doc: `~/Work/clawdio/docs/v2-vision.md` (historical context)
