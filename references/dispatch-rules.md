# Dispatch Rules

Cross-cutting rules for agents and skills that dispatch subagents, load other
skills, or interact with users. This file is the portability boundary between
Claude Code and Codex; keep client-specific mechanics here instead of copying
them into every workflow.

## Canonical sources

- `agents/*.md` contains specialist behaviour. Do not duplicate those prompts in
  Codex adapters or custom-agent files.
- `skills/*/SKILL.md` contains workflow behaviour shared by both clients.
- This file maps those logical agents and skills onto the tools exposed by the
  active client.

Relative paths in a skill are resolved from that skill's `SKILL.md`, not from
the user's working repository.

## Agent dispatch

Dispatch by role, not by a hard-coded tool name.

### Claude Code

Use the Agent tool with `subagent_type: "clawdio:<agent>"`. Never pass `name`:
named Claude agents enter mailbox mode and can sit idle. Track the returned
`agentId`.

Each agent's `tools:` frontmatter is its allowlist. Without one, a subagent
inherits every built-in and MCP tool schema in the session, which can exceed
300,000 tokens and is re-read on every call. Only the router holds `Agent`, so
specialists cannot fan out on their own.

### Codex

Codex plugins discover skills and hooks, but not Claude's `agents/*.md` files as
custom agents. The clawdio router therefore treats each Markdown agent as a
canonical prompt resource:

1. Resolve `../agents/<agent>.md` and this file to absolute paths from the
   plugin root. From `skills/router/SKILL.md`, those paths are
   `../../agents/<agent>.md` and `../../references/dispatch-rules.md`.
2. Spawn a built-in Codex subagent and tell it to read this file first, then the
   selected agent file, before doing the task. Pass the user's full issue or PR
   context unchanged.
3. Use `worker` for implementation, feedback fixes, tests, docs, and isolated
   shipping work; `explorer` for read-only investigation; and `default` for
   review, verification, triage, refinement, and release notes. Codex ignores
   the `tools:` frontmatter; this role choice is the equivalent restriction.
4. Do not pin a model or reasoning effort unless the user explicitly asks.

If the runtime cannot spawn subagents, run a single-agent version of the
workflow and say that the fanout was unavailable. Never claim that specialists
ran when they did not.

Only run write-heavy agents concurrently when each has an isolated worktree.
Use native worktree isolation when the client exposes it; otherwise create and
verify separate git worktrees before dispatch. Pass each manual worktree's
absolute path to its worker and require that path as the working directory for
every command. If the adapter cannot guarantee the starting directory, the
worker must verify it with `git rev-parse --show-toplevel` before editing. Run
the writers serially if any of those checks fail.

## Dispatch prompts and reports

A subagent re-reads its whole context on every call, so everything in a
dispatch is paid for on every turn of that agent.

- Pass facts that earlier agents or verifiers established as established, with
  their source. Ask for a re-check of one specific claim only when you have
  reason to doubt it; never ask an agent to re-verify every number and date.
- State a report limit as a shape: named fields, or a maximum number of lines
  or bullets. Never as a character count: agents that measure their own report
  redraft it in a loop.

## User decisions

Use the active client's structured user-input control when one is available.
In Claude Code this is `AskUserQuestion`. In Codex, use its user-input control
when exposed; otherwise ask one concise plain-text question and wait. Never
pretend a clickable choice was shown.

This applies to post/edit/don't-post, draft/ready, next-step suggestions, issue
selection, and merge confirmation.

### Externally visible writes

Any write others can see, and that is awkward to undo, needs explicit user
approval in the turn it happens: posting a review or comment, closing a PR,
merging, deleting a branch, and pushing to a branch we do not own. A verdict, a
plan, or an earlier confirmation is not that approval. Skills name which of
these they perform and point here rather than restating the rule.

### Issue writes

An issue has no head branch, so the PR provenance test below does not apply to
one. Gate issue writes on what the write destroys and on how many issues it
touches.

| Write | Approval |
|-|-|
| Add or remove one label, or assign or unassign, on a single issue | None. Ordinary maintainer work, and gating it makes the claim and ship flows unusable. |
| Overwrite an issue body with `gh issue edit --body` | In the turn it happens. Show the replacement text first; the old body is not recoverable from the API. |
| Close or reopen an issue | In the turn it happens |
| Post an issue comment | In the turn it happens, under Externally visible writes above |
| Any write touching more than one issue in one turn, whatever its type | In the turn it happens. List every issue number in the prompt. |

The cardinality ceiling counts the turn, not the command. A loop over ten issue
numbers is a bulk write even though each iteration edits one issue. So is one
label edit from each of ten workers dispatched together: count the issues the
dispatch will touch in total, not the issues any single agent can see.

## PR provenance

Establish who owns a pull request's head branch before dispatching anything that
writes to it. One call:

```bash
gh pr view <number> --json isCrossRepository,maintainerCanModify,authorAssociation,headRepositoryOwner,headRefName
```

| Result | Classification | What is allowed |
|-|-|-|
| `isCrossRepository: false` | ours | Full workflow, unchanged |
| `isCrossRepository: true` and `maintainerCanModify: true` | external, technically pushable | Review, comment, suggested changes. Record the flag and state it. |
| `isCrossRepository: true` and `maintainerCanModify: false` | external, hands off | Review, comment, suggested changes |

On any external PR the offered next steps are exactly two: review only and then
stop, or GitHub suggested changes on the diff. Never offer address-feedback, a
local rebase, or a force-push, and do not offer them behind a confirmation
either. `maintainerCanModify: true` means we could push to the contributor's
branch, not that we should. Push to a fork only when the user asks for it
unprompted, and name whose branch is being written to before doing it.

This gates writes to the head branch. Merging an approved fork PR into a base
repository we own is normal and unaffected.

Closing or pushing to someone else's PR falls under Externally visible writes
above. Approve it every time.

## Skill loading

Treat a namespaced skill as a capability request, not as an assumption that a
particular third-party plugin is installed.

Load a skill at the step that needs it, not all up front: a loaded skill is
re-read on every later call.

1. Prefer the exact namespaced skill named by the workflow.
2. If it is unavailable, use an installed skill that clearly provides the same
   capability.
3. If no equivalent is installed, use the local agent or skill procedure where
   it is self-contained. State which optional enhancement was unavailable.
4. Do not invoke an unrelated bare skill merely because its short name matches.

The Claude package declares `agent-skills` as a dependency. On clients where
that exact provider is unavailable, Clawdio's agent definitions contain the
baseline process: continue with it when an equivalent TDD, review, security,
debugging, or git skill is absent.

The Claude package also declares `kdt`; other clients may not have it. When its
external workflows are absent, use these local compositions rather than
copying kdt into this repository:

| Requested capability | Portable fallback |
|-|-|
| `kdt:feature-design` | refine agent, then docs agent |
| `kdt:feature-implement` | implement agent |
| `kdt:pr-closes-issue` | code-reviewer plus test-verifier |
| `kdt:external-contribs` | `clawdio:next` with external-contribution scope |

### Skill roster

Every skill the router may invoke, with the namespace that must be used:

| Namespace | Skills |
|-|-|
| `clawdio:` | `next`, `ship`, `pluck`, `issues`, `pr-description`, `doc-sync`, `review-coordination`, `verify-findings`, `merge-gate`, `worktree-recovery`, `parallel-ship` |
| `kdt:` | `feature-design`, `feature-implement`, `pr-closes-issue`, `external-contribs` |

A name outside this roster is not a clawdio skill. Resolve it before invoking it.

### Invocation syntax

- Claude Code: invoke the full name through the Skill tool, for example
  `clawdio:ship`; never shorten it to `ship` or `/ship`. A bare name can resolve
  to a different plugin's skill.
- Codex: load or request the installed namespaced skill using the skill
  mechanism exposed by the client. Preserve the `clawdio:` or external plugin
  namespace when the client displays one.

If loaded content does not match the requested capability -- `clawdio:next`
reading CONTRIBUTING.md instead of querying GitHub, say -- you invoked the wrong
skill. Stop and resolve the correct namespaced name before continuing.
