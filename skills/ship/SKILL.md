---
description: Full lifecycle skill for shipping an issue. Implements, pushes, creates PR, self-reviews, addresses issues, and prepares for merge. Use when the user says "ship this" or "ship #42".
---

# Ship

End-to-end lifecycle for shipping an issue to a merged PR.

## Steps

1. **Implement.** Dispatch the implement agent on the issue. Wait for completion.
2. **Push and PR.** Push the branch via `git push -u origin HEAD`. Create the PR via `gh pr create` following the pr-description skill format. Link the issue.
3. **Self-review.** Dispatch the review agent on the PR you just created. Read the findings.
4. **Fix.** If the review found real issues, fix them. Commit and push.
5. **Report.** Tell the user: PR is ready for team review. Link to the PR.

Do NOT merge automatically on team repos. The user decides when to merge after team review.

For personal repos (if the user explicitly says "ship and merge"), add a final merge step via `gh pr merge --squash`.
