# Contributing

How to add agents, skills, and hooks to clawdio.

## Development workflow

1. Edit files in the clawdio repo
2. Test locally: `claude --plugin-dir /path/to/clawdio --agent clawdio:router`
3. Reload without restarting: `/reload-plugins` inside an active session
4. Commit, push, **bump version in plugin.json**, then: `claude plugin update clawdio@jasonmadigan-clawdio`

Version bumps are required for updates to be picked up. Use patch bumps (0.1.x) for iteration.

## Writing agents

Agents are markdown files in `agents/`. One file per agent.

### Format

```markdown
---
name: agent-name
description: One sentence. What it does and when to use it.
---

# Agent Name

One sentence role statement.

## Process

Numbered steps or gated phases. Use decision trees for classification logic.

## Anti-patterns

Table of common mistakes and their fixes.

## Rules

Hard constraints the agent must follow.
```

### Patterns to use

**Gated phases** for multi-step workflows. Group steps into phases with verification checklists between them:

```markdown
### Phase 1: Understand
1. Read the issue...

### Phase 2: Plan
2. State your approach...

- [ ] Approach covers all acceptance criteria
- [ ] No scope beyond what the issue asks
```

**Decision trees** for classification and triage logic. Use ASCII trees:

```
Input
├── Condition A?
│   └── Action A
├── Condition B?
│   └── Action B
└── Neither?
    └── Ask the user
```

**Anti-pattern tables** for common mistakes. Two columns: Problem and Fix:

```markdown
| Problem | Fix |
|-|-|
| Doing X without checking Y | Always check Y first |
```

**Severity labels** for review agents. Use consistent labels across all reviewers:

| Label | Meaning | Action |
|-|-|-|
| Critical | Blocks merge | Must fix |
| Important | Should be addressed | Should fix |
| Nit | Minor, optional | Author's call |

**Verification checklists** mid-process, not just at the end. Use markdown checkboxes:

```markdown
- [ ] All tests pass
- [ ] No unrelated changes
```

**Cross-skill references** to agent-skills where relevant:

```markdown
Invoke the `agent-skills:test` skill for TDD.
```

### Conventions

- As short as possible, ideally. Every line should earn its place.
- Process steps should be concrete actions, not vague guidance.
- Rules should be things the agent would otherwise get wrong.
- The description field is what Claude uses to decide when to dispatch this agent. Make it precise.
- British English. No emojis. No AI-sounding prose.

### Worktree-isolated agents

Agents dispatched with `isolation: "worktree"` get their own git worktree. Conventions:

- The agent must not `cd` outside its working directory or reference files in the main worktree.
- Include a "Constraint: stay in your worktree" section at the top of the agent definition.
- Use a structured output format (e.g. `RESULT: complete`, `PR_URL: ...`) so the router can parse results programmatically.
- The agent cannot dispatch subagents (no Agent tool access). It can invoke skills.
- Worktrees are preserved if the agent made changes, cleaned up if not. The agent does not manage its own worktree lifecycle.

### When to use an agent vs a skill

- **Agent**: isolated task with its own context. Needs to read code, make decisions, produce output.
- **Skill**: cross-cutting knowledge that any agent or session can invoke. Templates, checklists, conventions.

Rule of thumb: if it _does work_, it's an agent. If it _knows things_, it's a skill.

### Subagent limitations

Subagents cannot spawn sub-subagents. They don't have access to the Agent tool. This means:
- Only the router (top-level agent) can dispatch other agents
- Agents that need to coordinate multiple specialists must be restructured so the router does the fanout
- Subagents CAN invoke skills (skills load into context, they don't need the Agent tool)

## Writing skills

Skills live in `skills/<name>/SKILL.md`. One directory per skill.

### Format

```markdown
---
description: One sentence. What it does and when it should be invoked.
---

# Skill Name

What this skill provides.

## Process / Content

Steps, checklists, or reference material.

## Output format

Exact format specification with examples.

## Anti-patterns

Common mistakes table.
```

### Skill arguments

Skills can accept arguments via the Skill tool's `args` parameter, passed as a single string.

- Document accepted args in an **Arguments** section immediately after the skill heading, before the process.
- Use a table: arg name, form (positional/flag/named), example.
- Support both positional (`ship #42`) and named (`ship --issue #42`) where it makes sense.
- The skill instructions tell Claude how to parse the args string. No framework needed.
- Args are for common cases. Complex orchestration should use conversation context.

Example:

```markdown
## Arguments

| Arg | Form | Example |
|-|-|-|
| issue ref | positional or `--issue` | `ship #42` |
| `--resume` | flag | Resume in-progress workflow |
```

### Workflow state

Workflow skills (multi-phase, resumable) can persist state to memory between sessions.

- Write state to `memory/workflow_<skill>_<branch>.md` after each phase gate.
- Use standard memory frontmatter (`name`, `description`, `type: project`).
- Check for existing state at skill start. Offer to resume or start fresh.
- Clean up on completion: delete the state file and remove from `MEMORY.md` index.
- State files are project-scoped (in the project memory directory), not global.

State file body should be simple key-value pairs: phase, issue, branch, PR URL, timestamp.

### Conventions

- The description field drives automatic invocation. Be specific about trigger phrases.
- Lead with the rule or action. Details and rationale below.
- Skills are loaded into the caller's context window, so keep them focused.
- Reference via `/clawdio:skill-name` in conversations.
- Include output format examples that are exact, not suggestive. Agents interpret loose formats liberally.

## Writing hooks

Hooks are defined in `hooks/hooks.json`. Deterministic shell commands at lifecycle events.

### Lifecycle events

- **PreToolUse**: runs before a tool executes. Exit code 2 blocks the tool.
- **PostToolUse**: runs after a tool executes.

### Available environment variables

- `CLAUDE_FILE_PATH`: the file being written/edited (for Write/Edit matchers)

### Conventions

- Hooks must be fast. They run on every matching tool use.
- Hooks must be deterministic. No LLM calls, no network requests.
- Use `2>/dev/null` for optional tools. Missing prettier should fail silently.
- Test by deliberately triggering: try writing to `.env` and verify it's blocked.

## Personal agent overrides

Plugin agents can be overridden by placing a file with the same name in `~/.claude/agents/`. Personal agents take precedence.

Use this for domain-specific reviewers that contain proprietary knowledge or team-specific conventions.

## Naming

- Agent names: lowercase, hyphenated. Match filename to `name` field.
- Skill names: lowercase, hyphenated directory name.
- Keep names short. `review` not `pull-request-review-coordinator`.

## Companion plugin

[agent-skills](https://github.com/addyosmani/agent-skills) provides cross-cutting development skills (TDD, debugging, security hardening, code review, spec-driven development). Clawdio agents reference these skills where relevant. Install it alongside clawdio.
