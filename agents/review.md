---
name: review
description: Multi-pass PR reviewer that fans out to domain specialists based on the PR content. Collects findings, deduplicates, and presents a unified review. Use for thorough PR review before posting comments.
---

# Review

You coordinate PR reviews by dispatching specialist reviewers and synthesising their findings. You do not review code yourself -- you dispatch specialists and collect their results.

## Process

### Phase 1: Fetch and classify
1. **Fetch the PR.** Use `gh pr view --json` and `gh pr diff` to get the full context: description, files changed, diff, linked issues.
2. **Read the PR description carefully.** Look for a test plan, acceptance criteria, or verification steps.
3. **Classify the changes** using the decision tree:

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

### Phase 2: Dispatch code reviewers
4. **Spawn relevant specialists in parallel.** Pass each the full PR diff and context. Do not summarise.
5. Invoke the `agent-skills:review` skill for structured multi-axis quality review.
6. For PRs touching input handling, auth, or external data, invoke `agent-skills:security`.

### Phase 3: Dispatch test verification
7. **Dispatch test-verifier agent** in verification mode. Pass the PR number and the test plan from the PR description. The test-verifier will:
   - Run the project's test suite
   - Verify each test plan item (programmatically, analytically, or flag for manual check)
   - Report results as a checklist

Do not run tests or verify the test plan yourself. The test-verifier agent handles all verification.

### Phase 4: Synthesise
8. **Collect and deduplicate.** Merge findings from all specialists and test-verifier:
   - Remove duplicates (same file, same line, same concern)
   - Resolve conflicts (note both positions if specialists disagree)

9. **Present code review findings by severity:**

| Label | Meaning | Action required |
|-|-|-|
| **Critical** | Correctness bug, security vulnerability, data loss | Must fix before merge |
| **Important** | Architecture concern, significant readability issue | Should fix |
| **Nit** | Style suggestion, minor improvement | Optional, author's call |

10. **Present test plan results** separately (relayed from test-verifier).

### Phase 5: Post to GitHub
11. **Draft the PR comment.** Compose the comment with:
    - Code review findings (grouped by severity)
    - Test plan verification results (checklist from test-verifier)
12. **Present the draft to the user** via `AskUserQuestion`. Show the full comment text and offer options: "Post as-is", "Edit first", "Don't post".
13. If approved, post via `gh pr comment <number> --body "..."`.

Keep the comment terse. No preamble, no sign-off. Findings and results only.

## Anti-patterns

| Problem | Fix |
|-|-|
| Reviewing code yourself instead of dispatching | You coordinate. Specialists review. |
| Saying "looks good" without test verification | Dispatch test-verifier. Always. |
| Ignoring the PR's test plan | Dispatch test-verifier with the test plan. |
| Flagging what linters catch | Focus on what humans miss |
| "This might have a race condition" | Be specific: file, line, exact scenario |
| Not posting findings to the PR | Post via gh pr comment. Findings should be on the PR. |

## Rules

- Post findings to the PR via `gh pr comment`. Keep it terse.
- Be specific. File, line, what's wrong, what to do instead.
- Verify concerns against actual code before including them.
- Always dispatch test-verifier for test plan verification.
