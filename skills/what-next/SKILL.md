---
description: Scans GitHub and Jira for actionable work. Shows issues assigned to you, PRs needing review, your open PRs and their status, and open Jira tickets. Use when the user asks "what's on?", "what should I work on?", or "what next?".
---

# What Next

Find actionable work across GitHub and Jira.

## Step 1: Query GitHub

Detect the repo, then run all three queries:

```bash
REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner')

gh search issues --assignee=@me --state=open --repo="$REPO" --json number,title,labels,updatedAt,url --limit 20

gh search prs --review-requested=@me --state=open --repo="$REPO" --json number,title,author,updatedAt,url --limit 20

gh pr list --author @me --json number,title,updatedAt,url,reviewDecision --limit 20
```

For "what's on everywhere" or "across all repos", drop `--repo` and replace `gh pr list` with `gh search prs --author=@me --state=open`.

## Step 2: Query Jira

If the Atlassian MCP server is available, also query Jira:

```
jira_search with JQL: assignee = currentUser() AND status != Done ORDER BY updated DESC
```

Include open Jira tickets in the results under their own section. Show key, summary, status, priority, and project.

If the Atlassian MCP server is not available, skip this step silently.

### Jira project to GitHub org mapping

When scoping results to the current repo, use this mapping to show relevant Jira tickets:

| Jira project | GitHub org/repos |
|-|-|
| CONNLINK | Kuadrant/* (kuadrant-operator, mcp-gateway, etc.) |

If the current repo is in the Kuadrant org, include CONNLINK tickets. For repos not in this mapping, show all Jira tickets without filtering.

## Step 3: Format

Present results in markdown tables. Group by priority (highest first):

1. **Address feedback** -- my PRs where `reviewDecision` is `CHANGES_REQUESTED`
2. **Review** -- PRs requesting my review
3. **Merge** -- my PRs where `reviewDecision` is `APPROVED`
4. **My PRs** -- my open PRs where `reviewDecision` is `REVIEW_REQUIRED`
5. **Implement** -- GitHub issues assigned to me
6. **Jira** -- open Jira tickets assigned to me

Skip sections with no results.

Every table uses three columns. The first column is a markdown link built from the `url` field in the query results. Example row: `| [#30](https://github.com/org/repo/issues/30) | Title here | detail |`

For Jira tickets, link to the Jira URL: `| [PROJ-123](https://site.atlassian.net/browse/PROJ-123) | Title | status, priority |`

## Step 4: Recommend

Suggest what to do first. Offer to pull up the top item.
