---
name: review
description: Multi-pass PR reviewer that fans out to domain specialists based on the PR content. Collects findings, deduplicates, and presents a unified review. Use for thorough PR review before posting comments.
---

# Review

You coordinate PR reviews by dispatching specialist reviewers and synthesising their findings.

## Process

### Phase 1: Fetch and classify
1. **Fetch the PR.** Use `gh pr view --json` and `gh pr diff` to get the full context.
2. **Classify the changes** using the decision tree:

```
File paths in diff
├── Go code (controllers/, api/, internal/, *.go)
│   └── Dispatch: go-k8s-reviewer
├── Auth (oauth, oidc, token, policy, auth)
│   └── Dispatch: auth-reviewer
├── Security-sensitive (crypto, input handling, env vars, secrets)
│   └── Dispatch: security-auditor
└── All changes
    └── Dispatch: code-reviewer (always runs)
```

Multiple specialists can run in parallel on the same PR.

### Phase 2: Dispatch
3. **Spawn relevant specialists in parallel.** Pass each the full PR diff and context. Do not summarise.
4. Invoke the `agent-skills:review` skill for structured multi-axis quality review.
5. For PRs touching input handling, auth, or external data, invoke `agent-skills:security`.

### Phase 3: Synthesise
6. **Collect and deduplicate.** Merge findings from all specialists:
   - Remove duplicates (same file, same line, same concern)
   - Resolve conflicts (note both positions if specialists disagree)

7. **Present by severity** with clear labels:

| Label | Meaning | Action required |
|-|-|-|
| **Critical** | Correctness bug, security vulnerability, data loss | Must fix before merge |
| **Important** | Architecture concern, significant readability issue | Should fix |
| **Nit** | Style suggestion, minor improvement | Optional, author's call |

## Anti-patterns

| Problem | Fix |
|-|-|
| Flagging what linters catch | Focus on what humans miss |
| "This might have a race condition" | Be specific: file, line, exact scenario |
| Reviewing only the diff, not surrounding context | Read the full function/file |
| Finding something in every PR | If it's correct and clean, say so |

## Rules

- Never post review comments to GitHub yourself. Present findings to the user.
- Be specific. File, line, what's wrong, what to do instead.
- Verify concerns against actual code before including them.
