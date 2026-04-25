# Kickoff

This repo is a Claude Code plugin called **workbench**. It replaces a custom Go orchestrator (clawdio) with native Claude Code primitives: agents, skills, hooks, and MCP configs.

## What we're building

A personal SDLC toolkit where I talk to a **router agent** and it handles everything. "What's on?" shows me priorities. "Ship #42" dispatches an implement agent, self-reviews, pushes, and creates a PR. "Review this PR" fans out to domain specialist reviewers in parallel.

The key insight: the bottleneck was never orchestration infrastructure -- it was agent reliability. Better agents beat better orchestration.

## Architecture

Router agent -> specialist subagents -> skills for cross-cutting knowledge -> hooks for guardrails.

Read `docs/architecture.md` for full context and `docs/grill-findings.md` for the structured interview that led to these decisions.

## What exists

- 9 agent definitions in `agents/` (router, implement, review, triage, refine, address-feedback, release-notes, test-writer, docs)
- 3 skills in `skills/` (what-next, ship, pr-description)
- Empty hooks skeleton
- Plugin manifest

## What's next

1. **Test the router.** Install the plugin (`claude plugin install .` or `claude --plugin-dir .`), invoke the router, see if the dispatch pattern works.
2. **Hone the agents.** The current definitions are first drafts. Run them on real tasks and iterate based on actual output quality.
3. **Add domain specialists.** Go/K8s reviewer and auth/policy reviewer live in `~/.claude/agents/` (not public). Wire the review agent to dispatch them.
4. **Borrow from agent-skills.** Review [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) for skills worth adopting (TDD, debugging, incremental implementation, spec-driven development).
5. **Add hooks.** Lint-on-edit, block .env writes, format-on-save.
6. **Wire MCP.** GitHub MCP server config for issue/PR operations.
7. **Build missing skills.** Commit conventions, security checklist, review rubric.

## Constraints

- Vertex AI only (no direct Anthropic API). Set `CLAUDE_CODE_USE_VERTEX=1` etc.
- British English. No emojis. Terse docs.
- Domain specialist agents (named after real people) stay in `~/.claude/agents/`, never in the public repo.
