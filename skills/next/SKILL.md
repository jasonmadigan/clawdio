---
description: Scans GitHub and Jira for actionable work. Shows issues assigned to you, PRs needing review, your open PRs and their status, and open Jira tickets. Use when the user asks "what's on?", "what should I work on?", or "what next?".
---

# Next

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

## Step 3: Repo activity

Regardless of OWNERS, check for open PRs in the repo that might need attention. These are PRs not authored by the user that have no reviews yet:

```bash
gh pr list --state open --json number,title,author,updatedAt,url,reviewDecision,reviewRequests --limit 20
```

Filter to PRs where:
- `author.login` is not the current user
- `reviewDecision` is empty or `REVIEW_REQUIRED` (no reviews submitted yet)

Exclude any PRs already captured in step 1 (requesting your review) or step 2 (component ownership).

These go into a **Repo activity** section — PRs that exist in the repo and may need a reviewer. This catches PRs on small teams where explicit review requests aren't always used.

If no unreviewed PRs from others exist, skip this step silently.

## Step 4: Query Jira

If the Atlassian MCP server is available, run two Jira queries:

**Assigned to me:**
```
jira_search with JQL: assignee = currentUser() AND status != Done ORDER BY updated DESC
```

**Contributor (custom field):**
```
jira_search with JQL: cf[10466] = currentUser() AND status != Done ORDER BY updated DESC
```

Merge results, deduplicating by issue key (an issue can appear in both). Mark contributor-only issues with "(contributor)" in the output so the user can distinguish ownership from involvement.

Include open Jira tickets in the results under their own section. Show key, summary, status, priority, and project.

If the Atlassian MCP server is not available, skip this step silently.

### Jira project to GitHub org mapping

When scoping results to the current repo, use this mapping to show relevant Jira tickets:

| Jira project | GitHub org/repos |
|-|-|
| CONNLINK | Kuadrant/* (kuadrant-operator, mcp-gateway, etc.) |

If the current repo is in the Kuadrant org, include CONNLINK tickets. For repos not in this mapping, show all Jira tickets without filtering.

## Step 5: Format

Present results in markdown tables. Group by priority (highest first):

1. **Address feedback** -- my PRs where `reviewDecision` is `CHANGES_REQUESTED`
2. **Review** -- PRs requesting my review
3. **Merge** -- my PRs where `reviewDecision` is `APPROVED`
4. **My PRs** -- my open PRs where `reviewDecision` is `REVIEW_REQUIRED`
5. **Implement** -- GitHub issues assigned to me
6. **Component owner** -- open PRs and unassigned issues in repos where I am an OWNERS approver/reviewer
7. **Repo activity** -- open PRs from others with no reviews yet
8. **Jira** -- open Jira tickets assigned to me

Skip sections with no results.

Every table uses three columns. The first column is a markdown link built from the `url` field in the query results. Example row: `| [#30](https://github.com/org/repo/issues/30) | Title here | detail |`

For Jira tickets, link to the Jira URL: `| [PROJ-123](https://site.atlassian.net/browse/PROJ-123) | Title | status, priority |`

## Step 6: Recommend

Suggest what to do first. Offer to pull up the top item.
