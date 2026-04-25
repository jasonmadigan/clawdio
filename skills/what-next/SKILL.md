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

2. Run these queries scoped to that repo:

```bash
REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner')

# issues assigned to me
gh search issues --assignee=@me --state=open --repo="$REPO" --json number,title,labels,updatedAt,url --limit 20

# PRs needing my review
gh search prs --review-requested=@me --state=open --repo="$REPO" --json number,title,author,updatedAt,url --limit 20

# my PRs with review feedback
gh search prs --author=@me --state=open --review=changes_requested --repo="$REPO" --json number,title,updatedAt,url --limit 20

# my PRs that are approved
gh search prs --author=@me --state=open --review=approved --repo="$REPO" --json number,title,updatedAt,url --limit 20
```

If the user says "what's on everywhere" or "across all repos", drop the `--repo` filter and search globally.

3. Group by action type and present as a prioritised list:
   - Address feedback (unblock others) > Reviews requested (unblock others) > Approved PRs (merge and close) > Implementation (new work)

4. Omit empty sections.

## Output format

Two lines per item: summary, then the `url` field on its own line. Include priority labels where present.

```
Implement (2)
  #30  Max cutout depth calculation                        2d ago
       https://github.com/tracefinity/tracefinity/issues/30
  #29  Cutout drag and drop with auto-size grid            2d ago
       https://github.com/tracefinity/tracefinity/issues/29

Review (1)
  #456  Add rate limit header support                      alice, 2h ago
        https://github.com/org/repo/pull/456
```

After the list, suggest what to do first. Offer to pull up the top item.
