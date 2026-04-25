---
description: Scans GitHub for actionable work in the current repo. Shows issues assigned to you, PRs needing review, your open PRs and their status. Use when the user asks "what's on?", "what should I work on?", or "what next?".
---

# What Next

Find actionable work for the current repo.

## Step 1: Query

Detect the repo, then run all three queries:

```bash
REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner')

gh search issues --assignee=@me --state=open --repo="$REPO" --json number,title,labels,updatedAt,url --limit 20

gh search prs --review-requested=@me --state=open --repo="$REPO" --json number,title,author,updatedAt,url --limit 20

gh pr list --author @me --json number,title,updatedAt,url,reviewDecision --limit 20
```

For "what's on everywhere" or "across all repos", drop `--repo` and replace `gh pr list` with `gh search prs --author=@me --state=open`.

## Step 2: Format

Present results in markdown tables. Group by priority (highest first):

1. **Address feedback** -- my PRs where `reviewDecision` is `CHANGES_REQUESTED`
2. **Review** -- PRs requesting my review
3. **Merge** -- my PRs where `reviewDecision` is `APPROVED`
4. **My PRs** -- my open PRs where `reviewDecision` is `REVIEW_REQUIRED`
5. **Implement** -- issues assigned to me

Skip sections with no results.

Every table uses three columns. The first column is a markdown link built from the `url` field in the query results. Example row: `| [#30](https://github.com/org/repo/issues/30) | Title here | detail |`

Example output:

**My PRs (1)**

| # | Title | Detail |
|-|-|-|
| [#32](https://github.com/org/repo/pull/32) | Fix drag glitch | awaiting review, today |

**Implement (1)**

| # | Title | Detail |
|-|-|-|
| [#30](https://github.com/org/repo/issues/30) | Max cutout depth | workflow:ship, 2d ago |

## Step 3: Recommend

Suggest what to do first. Offer to pull up the top item.
