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

Every item MUST include a clickable GitHub URL. Build URLs from the repo and number: `https://github.com/{owner}/{repo}/issues/{number}` for issues, `https://github.com/{owner}/{repo}/pull/{number}` for PRs.

Include priority labels if present (P0, P1, priority/high, priority/critical).

Omit empty sections entirely. Don't show "Review (0)".

```
Review (2)
  #456  Add rate limit header support        alice, 2h ago
        https://github.com/org/repo/pull/456
  #89   Fix webhook retry logic              bob, 1d ago
        https://github.com/org/repo/pull/89

Address feedback (1)
  #450  Policy attachment refactor            2 comments, 3h ago
        https://github.com/org/repo/pull/450

Merge (1)
  #87   Update SDK dependency                 approved, CI passing
        https://github.com/org/repo/pull/87

Implement (3)
  #460  Support wildcard hostnames            priority/high
        https://github.com/org/repo/issues/460
  #30   Max depth calculation
        https://github.com/org/repo/issues/30
  #43   Post-complete hooks
        https://github.com/org/repo/issues/43
```

After the list, suggest what to do first with a one-line recommendation. Offer to pull up the top priority item.
