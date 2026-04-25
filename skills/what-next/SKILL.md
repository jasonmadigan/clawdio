---
description: Scans GitHub for actionable work in the current repo. Shows issues assigned to you, PRs needing review, your open PRs and their status. Use when the user asks "what's on?", "what should I work on?", or "what next?".
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

# my open PRs (includes review status)
gh pr list --author @me --json number,title,updatedAt,url,reviewDecision --limit 20
```

If the user says "what's on everywhere" or "across all repos", drop the `--repo` filter from search commands and use `gh search prs --author=@me --state=open` instead of `gh pr list`.

3. Group the results and present as a prioritised list.

## Output format

Use the SAME table format for every section. All tables must have identical structure: three columns, markdown link in the first column. No exceptions. Do not vary the format between sections.

The first column MUST be a markdown link using the `url` field: `[#30](https://github.com/...)`.

Omit sections with no results. Include priority labels where present.

**Priority order (most urgent first):**

1. **Address feedback** -- my PRs with `reviewDecision: CHANGES_REQUESTED`
2. **Review** -- PRs requesting my review
3. **Merge** -- my PRs with `reviewDecision: APPROVED`
4. **My PRs** -- my open PRs with `reviewDecision: REVIEW_REQUIRED` (awaiting review)
5. **Implement** -- issues assigned to me

Every section uses this exact table structure:

```markdown
**Address feedback (1)**

| # | Title | Detail |
|-|-|-|
| [#50](https://github.com/org/repo/pull/50) | Policy refactor | changes requested, 3h ago |

**Review (1)**

| # | Title | Detail |
|-|-|-|
| [#456](https://github.com/org/repo/pull/456) | Add rate limit header | alice, 2h ago |

**My PRs (1)**

| # | Title | Detail |
|-|-|-|
| [#32](https://github.com/org/repo/pull/32) | Fix drag glitch | awaiting review, today |

**Implement (2)**

| # | Title | Detail |
|-|-|-|
| [#30](https://github.com/org/repo/issues/30) | Max cutout depth calculation | 2d ago |
| [#29](https://github.com/org/repo/issues/29) | Cutout drag and drop with auto-size grid | 2d ago |
```

After the list, suggest what to do first. Offer to pull up the top item.
