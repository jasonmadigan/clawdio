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

## Step 2: Check component ownership

Check if the repo has a Kubernetes-style OWNERS file (root level):

```bash
gh api "repos/$REPO/contents/OWNERS" --jq '.content' 2>/dev/null | base64 -d
```

If the file exists, parse the YAML for `approvers` and `reviewers` lists. Get the current user's GitHub handle:

```bash
gh api user --jq '.login'
```

If the user appears in either list, they are a component owner. Query for open PRs and issues that are **not** already assigned to or requesting review from the user (those are already captured in step 1):

```bash
gh search prs --repo="$REPO" --state=open --json number,title,author,updatedAt,url,labels --limit 20

gh search issues --repo="$REPO" --state=open --no-assignee --json number,title,labels,updatedAt,url --limit 20
```

Filter out any results already shown in step 1 (same PR/issue number). These go into a new **Component owner** section in the output.

If there is no OWNERS file, or the user is not listed, skip this step silently.

## Step 3: Query Jira

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

## Step 4: Format

Present results in markdown tables. Group by priority (highest first):

1. **Address feedback** -- my PRs where `reviewDecision` is `CHANGES_REQUESTED`
2. **Review** -- PRs requesting my review
3. **Merge** -- my PRs where `reviewDecision` is `APPROVED`
4. **My PRs** -- my open PRs where `reviewDecision` is `REVIEW_REQUIRED`
5. **Implement** -- GitHub issues assigned to me
6. **Component owner** -- open PRs and unassigned issues in repos where I am an OWNERS approver/reviewer
7. **Jira** -- open Jira tickets assigned to me

Skip sections with no results.

Every table uses three columns. The first column is a markdown link built from the `url` field in the query results. Example row: `| [#30](https://github.com/org/repo/issues/30) | Title here | detail |`

For Jira tickets, link to the Jira URL: `| [PROJ-123](https://site.atlassian.net/browse/PROJ-123) | Title | status, priority |`

## Step 5: Recommend

Suggest what to do first. Offer to pull up the top item.
