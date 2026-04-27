---
description: Full lifecycle skill for shipping an issue. Implements, pushes, creates PR, self-reviews, addresses issues, and prepares for merge. Use when the user says "ship this" or "ship #42".
---

# Ship

End-to-end lifecycle for shipping an issue to a merged PR.

## Process

### Phase 1: Implement
1. Dispatch the implement agent on the issue. Wait for completion.

- [ ] All tests pass
- [ ] Implementation matches acceptance criteria
- [ ] No scope creep

### Phase 2: Pre-ship checks
2. Invoke `agent-skills:shipping-and-launch` for pre-ship checklist. Invoke `agent-skills:git-workflow-and-versioning` for commit conventions.

### Phase 3: Push and PR
3. Create a branch if not already on one:
   ```bash
   git checkout -b <issue-number>-<short-description>
   ```
3. Push: `git push -u origin HEAD`
4. Create the PR via `gh pr create` following the clawdio:pr-description skill format. Link the issue.

- [ ] PR description follows template (summary, linked issue, test evidence)
- [ ] Branch name is descriptive

### Phase 4: Self-review
5. Tell the router to review the PR you just created. The router will dispatch specialist reviewers (code-reviewer, test-verifier, and any domain specialists) in parallel.
6. If the review found real issues (Critical or Important), fix them. Commit and push.

- [ ] All Critical findings addressed
- [ ] All Important findings addressed
- [ ] Nits addressed if trivial, skipped if contentious

### Phase 5: Report
7. Tell the user: PR is ready for team review. Link to the PR.

## Decision tree: merge or wait?

```
PR ready
├── Personal repo + user said "ship and merge"?
│   └── Merge via gh pr merge --squash
├── Personal repo + user didn't say to merge?
│   └── Report PR link, let user decide
└── Team repo?
    └── Never merge automatically. Report PR link.
```

## Anti-patterns

| Problem | Fix |
|-|-|
| Merging on a team repo without asking | Never. The user decides after team review. |
| Skipping self-review | Always self-review. Catches obvious issues before team sees them. |
| Pushing without running tests | Tests must pass before push. |
| Creating a PR with a one-line description | Follow the clawdio:pr-description skill format. |
