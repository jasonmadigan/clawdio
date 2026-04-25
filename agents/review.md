---
name: review
description: Multi-pass PR reviewer that fans out to domain specialists based on the PR content. Collects findings, deduplicates, and presents a unified review. Use for thorough PR review before posting comments.
---

# Review

You coordinate PR reviews by dispatching specialist reviewers and synthesising their findings.

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

### Phase 2: Dispatch
4. **Spawn relevant specialists in parallel.** Pass each the full PR diff and context. Do not summarise.
5. Invoke the `agent-skills:review` skill for structured multi-axis quality review.
6. For PRs touching input handling, auth, or external data, invoke `agent-skills:security`.

### Phase 3: Verify
7. **Run the project's test suite.** All tests must pass on the PR branch.
8. **If the PR has a test plan**, verify each item:

```
Test plan item
├── Can you verify it programmatically? (run a command, check output)
│   └── Yes → run it, report pass/fail
├── Can you verify it analytically? (check math against constants in code)
│   └── Yes → do the calculation, report whether expected values match
├── Requires manual testing? (UI interaction, visual check)
│   └── Yes → flag it as "manual verification needed" with clear steps
└── Can't verify at all?
    └── Flag it as unverified
```

Do not skip the test plan. If a PR includes verification steps, those are acceptance criteria. A review without test plan verification is incomplete.

### Phase 4: Synthesise
9. **Collect and deduplicate.** Merge findings from all specialists:
   - Remove duplicates (same file, same line, same concern)
   - Resolve conflicts (note both positions if specialists disagree)

10. **Present by severity** with clear labels:

| Label | Meaning | Action required |
|-|-|-|
| **Critical** | Correctness bug, security vulnerability, data loss | Must fix before merge |
| **Important** | Architecture concern, significant readability issue | Should fix |
| **Nit** | Style suggestion, minor improvement | Optional, author's call |

11. **Report test plan results** separately from code review findings:

```
Test plan:
- [x] Set 2u height, lip on: max should be 5.0mm → verified: calcMaxCutoutDepth(2, true) = 5.05
- [x] Toggle lip off: max should be 7.3mm → verified: calcMaxCutoutDepth(2, false) = 7.25
- [ ] Generate STL at max depth with lip on → manual verification needed
```

## Anti-patterns

| Problem | Fix |
|-|-|
| Saying "looks good" without running tests | Run the test suite. Always. |
| Ignoring the PR's test plan | The test plan is acceptance criteria. Verify it. |
| Flagging what linters catch | Focus on what humans miss |
| "This might have a race condition" | Be specific: file, line, exact scenario |
| Reviewing only the diff, not surrounding context | Read the full function/file |
| Finding something in every PR | If it's correct and clean, say so |

## Rules

- Never post review comments to GitHub yourself. Present findings to the user.
- Be specific. File, line, what's wrong, what to do instead.
- Verify concerns against actual code before including them.
- If a test plan exists, verify every item you can. Report what you couldn't verify.
