# workbench

Personal Claude Code plugin for SDLC automation.

## Architecture

Router agent dispatches to specialist subagents based on the task. Skills provide cross-cutting knowledge. Hooks enforce guardrails.

```
you -> router -> specialist subagent(s) -> result
                    |
                    +-- skills (PR template, commit conventions, review rubric)
                    +-- hooks (lint, block .env, format)
                    +-- MCP (github)
```

## Structure

```
agents/          subagent definitions (.md)
skills/          on-demand skills (SKILL.md per directory)
hooks/           lifecycle hooks (hooks.json)
references/      supporting docs agents can read
```

## Conventions

- Agents: terse system prompts, under 300 lines. No waffle.
- Skills: progressive disclosure. Lead with the rule, details below.
- British English in all user-facing text.
- No emojis. No AI-sounding prose.
