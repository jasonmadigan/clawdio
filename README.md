# workbench

Claude Code plugin for SDLC automation. A router agent dispatches to specialist subagents based on the task. Skills provide cross-cutting workflow knowledge. Hooks enforce guardrails.

The premise: the bottleneck is never orchestration infrastructure -- it's agent reliability. This plugin invests in good agents, skills, and hooks that work natively in Claude Code, replacing a [custom Go orchestrator](https://github.com/jasonmadigan/clawdio) that was over-built for what it did.

## Install

```bash
# add the marketplace
claude plugin marketplace add jasonmadigan/workbench

# install the plugin (user scope, available in all repos)
claude plugin install workbench
```

For local development:

```bash
claude --plugin-dir /path/to/workbench
```

Reload after changes without restarting Claude:

```
/reload-plugins
```

## Dependencies

Install these separately -- workbench agents and skills reference them.

### Plugins

| Plugin | Install | What it provides |
|-|-|-|
| [agent-skills](https://github.com/addyosmani/agent-skills) | `claude plugin marketplace add addyosmani/agent-skills && claude plugin install agent-skills` | Security hardening, code review, TDD, debugging, git workflow, spec-driven development |
| [playwright](https://github.com/anthropics/claude-plugins-official) | `claude plugin install playwright` | Browser automation for UI test verification |

Workbench handles SDLC orchestration (router, specialists, shipping). agent-skills handles cross-cutting development practices. They complement each other.

### CLI tools

| Tool | Purpose | Used by |
|-|-|-|
| [`gh`](https://cli.github.com/) | GitHub issue/PR operations | implement, review, triage, refine, address-feedback, what-next, ship |

Must be authenticated (`gh auth login`).

### MCP servers

| Server | Purpose | Used by |
|-|-|-|
| GitHub MCP | Issue/PR comments, review threads | address-feedback |

## How it works

Talk to the **router** agent. It classifies your request and dispatches the right specialist.

```
you -> router -> specialist subagent(s) -> result
                    |
                    +-- skills (what-next, ship, pr-description)
                    +-- hooks (block secrets, lint, format)
```

### Typical workflows

**"What's on?"** -- the router invokes the `what-next` skill. It queries GitHub for issues assigned to you, PRs needing your review, PRs with feedback to address, and approved PRs ready to merge. Returns a prioritised list.

**"Ship #42"** -- the router invokes the `ship` skill. It dispatches the implement agent on the issue, pushes the branch, creates a PR following the `pr-description` template, dispatches the review agent for a self-review, fixes any findings, and reports back with a link to the PR.

**"Review this PR"** -- the router dispatches the review agent, which analyses the diff and fans out to specialist reviewers in parallel:

| Changes detected | Reviewer |
|-|-|
| Go code, controllers, CRDs | go-k8s-reviewer |
| Auth, OAuth, OIDC, tokens, policies | auth-reviewer |
| Crypto, input handling, secrets | security-auditor |
| General quality | code-reviewer |

Findings are collected, deduplicated, and presented by severity (must fix > should fix > consider).

**"Triage this issue"** -- the router dispatches the triage agent, which assesses readiness (requirements clarity, scope, dependencies, implementability) and recommends a workflow: implement directly, refine first, split into sub-issues, or flag for human review.

**"This issue is vague"** -- the router dispatches the refine agent, which explores the codebase, identifies gaps (missing acceptance criteria, edge cases, scope), and produces a structured specification with testable acceptance criteria.

## Agents

| Agent | Purpose |
|-|-|
| router | Task intake, classification, delegation. Never writes code. |
| implement | Takes a well-defined issue, writes code, runs tests, commits |
| review | Coordinates multi-pass PR review, fans out to domain specialists |
| code-reviewer | General code quality: correctness, readability, architecture, naming |
| security-auditor | Security review: injection, auth bypasses, secrets, crypto, OWASP |
| go-k8s-reviewer | Go idioms, concurrency, controller patterns, CRD conventions, RBAC |
| auth-reviewer | OAuth2/OIDC flows, token handling, policy evaluation, standards compliance |
| triage | Assesses issue readiness, labels, prioritises, recommends workflow |
| refine | Turns vague issues into implementable specs with acceptance criteria |
| address-feedback | Reads PR review comments, categorises, fixes, reports what needs human input |
| release-notes | Generates grouped release notes between git tags |
| test-writer | Finds coverage gaps, writes targeted tests matching project patterns |
| test-verifier | Verifies PR test plans: runs tests, checks criteria, drives browser for UI checks |
| docs | Writes and updates documentation. Verifies every example and path. |

## Skills

| Skill | Trigger | Purpose |
|-|-|-|
| what-next | "what's on?", "what next?" | Scans GitHub for issues, PRs, and feedback across repos |
| ship | "ship #42" | Full lifecycle: implement > push > PR > self-review > fix |
| pr-description | Creating a PR | PR body template: summary, linked issue, test evidence |

## Hooks

| Hook | Trigger | Purpose |
|-|-|-|
| block-env-writes | Before Write/Edit | Blocks writes to `.env`, credentials, `.pem`, `.key` files |
| format-on-save | After Write/Edit | Runs project formatter if configured (prettier, gofmt, clang-format) |
| lint-on-edit | After Write/Edit | Runs project linter if configured (eslint, golangci-lint) |

## Structure

```
agents/           subagent definitions (one .md per agent)
skills/           on-demand skills (SKILL.md per directory)
hooks/            lifecycle hooks (hooks.json)
references/       supporting docs agents can read
docs/             architecture decisions and project context
.claude-plugin/   plugin manifest and marketplace config
```

## Personalisation

The go-k8s-reviewer and auth-reviewer ship with generic definitions suitable for any Go/K8s or auth project. For domain-specific review depth, override them with personal versions in `~/.claude/agents/` -- personal agents take precedence over plugin agents.

Personal agent overrides stay out of this repo. They're your competitive advantage, not a shared concern.

## Development

See [docs/contributing.md](docs/contributing.md) for how to write agents, skills, and hooks.

Edit, test locally with `claude --plugin-dir .`, push, then `claude plugin update workbench@jasonmadigan-workbench`.

## Design

See [docs/architecture.md](docs/architecture.md) for the full design rationale, including why this is a plugin and not an orchestrator, the three-tier primitive location model, and future Agent SDK migration path.

See [docs/grill-findings.md](docs/grill-findings.md) for the structured interview that informed these decisions.
