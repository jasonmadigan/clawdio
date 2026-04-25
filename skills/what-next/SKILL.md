---
description: Scans GitHub for actionable work across configured repos. Shows issues assigned to you, PRs needing review, PRs with feedback to address. Use when the user asks "what's on?", "what should I work on?", or "what next?".
---

# What Next

Find actionable work across GitHub repos.

## Process

1. Run these `gh` queries:

```bash
# issues assigned to me, open
gh search issues --assignee=@me --state=open --json repository,number,title,labels,updatedAt --limit 20

# PRs needing my review
gh search prs --review-requested=@me --state=open --json repository,number,title,author,updatedAt --limit 20

# my PRs with review feedback
gh search prs --author=@me --state=open --review=changes_requested --json repository,number,title,updatedAt --limit 20

# my PRs that are approved (ready to merge)
gh search prs --author=@me --state=open --review=approved --json repository,number,title,updatedAt --limit 20
```

2. Group by action type:

- **Implement**: open issues assigned to me
- **Review**: PRs requesting my review
- **Address feedback**: my PRs with changes requested
- **Merge**: my PRs that are approved

3. Present as a prioritised list. Suggest what to do first based on:
- PRs with feedback (unblock others) > reviews requested (unblock others) > approved PRs (merge and close) > implementation (new work)

## Output format

```
Review (2)
  org/project-a#456  Add rate limit header support  (alice, 2h ago)
  org/project-b#89   Fix webhook retry logic        (bob, 1d ago)

Address feedback (1)
  org/project-a#450  Policy attachment refactor      (2 comments, 3h ago)

Merge (1)
  org/project-b#87   Update SDK dependency           (approved, CI passing)

Implement (3)
  org/project-a#460  Support wildcard hostnames      (ready, P1)
  personal/app#30    Max depth calculation           (ready)
  personal/tools#43  Post-complete hooks             (ready)
```
