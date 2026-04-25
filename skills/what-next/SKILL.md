---
description: Scans GitHub for actionable work in the current repo. Shows issues assigned to you, PRs needing review, PRs with feedback to address. Use when the user asks "what's on?", "what should I work on?", or "what next?".
---

# What Next

Find actionable work for the current repo.

## Process

1. Detect the current repo:

```bash
gh repo view --json nameWithOwner --jq '.nameWithOwner'
```

2. Run these `gh` queries scoped to that repo:

```bash
REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner')

# issues assigned to me, open
gh search issues --assignee=@me --state=open --repo="$REPO" --json repository,number,title,labels,updatedAt --limit 20

# PRs needing my review
gh search prs --review-requested=@me --state=open --repo="$REPO" --json repository,number,title,author,updatedAt --limit 20

# my PRs with review feedback
gh search prs --author=@me --state=open --review=changes_requested --repo="$REPO" --json repository,number,title,updatedAt --limit 20

# my PRs that are approved (ready to merge)
gh search prs --author=@me --state=open --review=approved --repo="$REPO" --json repository,number,title,updatedAt --limit 20
```

If the user says "what's on everywhere" or "across all repos", drop the `--repo` filter and search globally.

3. Group by action type:

- **Implement**: open issues assigned to me
- **Review**: PRs requesting my review
- **Address feedback**: my PRs with changes requested
- **Merge**: my PRs that are approved

4. Present as a prioritised list. Suggest what to do first based on:
- PRs with feedback (unblock others) > reviews requested (unblock others) > approved PRs (merge and close) > implementation (new work)

## Output format

```
Review (2)
  org/repo#456  Add rate limit header support  (alice, 2h ago)
  org/repo#89   Fix webhook retry logic        (bob, 1d ago)

Address feedback (1)
  org/repo#450  Policy attachment refactor      (2 comments, 3h ago)

Merge (1)
  org/repo#87   Update SDK dependency           (approved, CI passing)

Implement (3)
  org/repo#460  Support wildcard hostnames      (ready, P1)
  org/repo#30   Max depth calculation           (ready)
  org/repo#43   Post-complete hooks             (ready)
```
