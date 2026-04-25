# References

## Claude Code primitives

- **CLAUDE.md**: always-on context loaded at session start. Project conventions, build/test commands, architecture notes.
- **Skills**: `skills/<name>/SKILL.md`. On-demand knowledge loaded when Claude judges them relevant. Cross-cutting "how to do X" knowledge.
- **Subagents**: `agents/<name>.md`. Isolated workers with own context window, system prompt, tool allowlist. Delegation and context isolation.
- **Hooks**: `hooks/hooks.json`. Deterministic shell commands at lifecycle events (PreToolUse, PostToolUse). Guardrails the LLM can't skip.
- **MCP servers**: `.mcp.json`. Connector layer to external systems (GitHub, Jira, Slack, etc.).
- **Plugins**: bundle any of the above into a shareable unit. `.claude-plugin/plugin.json` manifest.

## Execution surfaces

The same skills and agent definitions run in:
1. **Claude Code CLI** (terminal or IDE extension) -- human is the orchestrator
2. **Claude Code in GitHub Actions** (`anthropic/claude-code-action@v1`) -- headless, webhook-triggered
3. **Agent SDK** (Python/TypeScript) -- embedded in custom applications

## Key repos

- [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) -- reference plugin, good skills to borrow
- [github/github-mcp-server](https://github.com/github/github-mcp-server) -- GitHub MCP server for issues, PRs, Actions
- [anthropics/claude-code-action](https://github.com/anthropics/claude-code-action) -- GitHub Actions integration

## Vertex auth

Environment variables for Vertex AI access:
```
CLAUDE_CODE_USE_VERTEX=1
ANTHROPIC_VERTEX_PROJECT_ID=<project-id>
CLOUD_ML_REGION=<region>
```

Works with Claude Code CLI, GitHub Actions, and Agent SDK. Does NOT work with Claude Managed Agents (Anthropic-hosted).
