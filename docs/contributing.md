# Contributing

How to add agents, skills, and hooks to workbench.

## Development workflow

1. Edit files in the workbench repo
2. Test locally: `claude --plugin-dir /path/to/workbench --agent workbench:router`
3. Reload without restarting: `/reload-plugins` inside an active session
4. Commit, push, then update the installed plugin: `claude plugin update workbench@jasonmadigan-workbench`

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

Numbered steps. What the agent does, in order.

## Rules

Bullet list. Hard constraints the agent must follow.
```

### Conventions

- Under 50 lines. If you need more, the agent is doing too much.
- Process steps should be concrete actions, not vague guidance. "Use `gh issue view` to get the full body" not "understand the issue".
- Rules should be things the agent would otherwise get wrong. Don't restate obvious behaviour.
- The description field is what Claude uses to decide when to dispatch this agent. Make it precise.
- British English. No emojis. No AI-sounding prose.

### When to use an agent vs a skill

- **Agent**: isolated task with its own context. Needs to read code, make decisions, produce output. Gets its own context window.
- **Skill**: cross-cutting knowledge that any agent or session can invoke. Templates, checklists, conventions. Loaded into the current context window.

Rule of thumb: if it _does work_, it's an agent. If it _knows things_, it's a skill.

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

The actual knowledge or steps.
```

### Conventions

- The description field drives automatic invocation. Claude reads it and decides whether to load the skill. Be specific about trigger phrases.
- Lead with the rule or action. Details and rationale below.
- Skills can include shell commands, templates, checklists -- anything an agent or session needs.
- Skills are loaded into the caller's context window, so keep them focused. A 500-line skill wastes context on every invocation.
- Reference via `/workbench:skill-name` in conversations.

### Supporting files

Skills can include additional files alongside SKILL.md (templates, reference docs). The SKILL.md can reference them with relative paths. Keep supporting files small.

## Writing hooks

Hooks are defined in `hooks/hooks.json`. They're deterministic shell commands that run at lifecycle events.

### Format

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "your shell command here"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "your shell command here"
          }
        ]
      }
    ]
  }
}
```

### Lifecycle events

- **PreToolUse**: runs before a tool executes. Exit code 2 blocks the tool. Use for guardrails (block sensitive file writes).
- **PostToolUse**: runs after a tool executes. Use for side effects (lint, format).

### Available environment variables

- `CLAUDE_FILE_PATH`: the file being written/edited (for Write/Edit matchers)
- Standard shell environment (PATH, HOME, etc.)

### Conventions

- Hooks must be fast. They run on every matching tool use. A slow hook degrades the entire session.
- Hooks must be deterministic. No LLM calls, no network requests, no prompts.
- Use `2>/dev/null` liberally. Missing tools (prettier not installed, golangci-lint not present) should fail silently, not error noisily.
- Test hooks by deliberately triggering them: try writing to a `.env` file and verify it's blocked.

## Personal agent overrides

Plugin agents can be overridden by placing a file with the same name in `~/.claude/agents/`. Personal agents take precedence.

Use this for domain-specific reviewers that contain proprietary knowledge or team-specific conventions you don't want in a public repo.

Example: the plugin ships a generic `go-k8s-reviewer.md`. You override it with a version in `~/.claude/agents/go-k8s-reviewer.md` that knows your specific controller patterns, CRD conventions, and team style preferences.

## Naming

- Agent names: lowercase, hyphenated. Match the filename to the `name` field in frontmatter.
- Skill names: lowercase, hyphenated directory name.
- Keep names short and descriptive. `review` not `pull-request-review-coordinator`.
