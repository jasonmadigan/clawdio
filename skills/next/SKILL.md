---
name: next
description: Scans GitHub and Jira for actionable work. Shows issues assigned to you, PRs needing review, your open PRs and their status, and open Jira tickets. Use when the user asks "what's on?", "what should I work on?", or "what next?".
---

# Next

Scan GitHub and Jira to find actionable work. Invoke via `clawdio:next`.

## Step 1: Query GitHub

Detect the repo with `gh repo view`, then run all three queries:

```bash
REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner')

gh search issues --assignee=@me --state=open --repo="$REPO" --json number,title,labels,updatedAt,url --limit 20

# if the above returns zero results, query the backlog
gh search issues --no-assignee --state=open --repo="$REPO" --json number,title,labels,updatedAt,url --limit 10 --sort updated

gh search prs --review-requested=@me --state=open --repo="$REPO" --json number,title,author,updatedAt,url --limit 20

gh pr list --author @me --json number,title,updatedAt,url,reviewDecision --limit 20
```

For "what's on everywhere" or "across all repos", drop `--repo` from the commands above and replace `gh pr list` with `gh search prs --author=@me --state=open`.

## Step 2: Check component ownership

Check if the repo has a Kubernetes-style `OWNERS` file at the repo root:

```bash
gh api "repos/$REPO/contents/OWNERS" --jq '.content' 2>/dev/null | base64 -d
```

If `OWNERS` exists, parse the YAML for `approvers` and `reviewers` lists. Get the current user's GitHub handle:

```bash
gh api user --jq '.login'
```

If the user appears in either list, they are a component owner for this repo. Query for open PRs and issues that are **not** already assigned to or requesting review from the user (those are already captured in step 1):

```bash
gh search prs --repo="$REPO" --state=open --json number,title,author,updatedAt,url,labels --limit 20

gh search issues --repo="$REPO" --state=open --no-assignee --json number,title,labels,updatedAt,url --limit 20
```

Filter out any results already shown in step 1 (same PR/issue number). These go into a **Component owner** section in the output.

If there is no `OWNERS` file, or the user is not listed, skip this step silently.

## Step 3: Repo activity

Regardless of `OWNERS`, check for open PRs in the repo that need attention. These are PRs not authored by the user that have no reviews yet:

```bash
gh pr list --state open --json number,title,author,updatedAt,url,reviewDecision,reviewRequests --limit 20
```

Filter the `gh pr list` output to PRs where:
- `author.login` is not the current user (compare against `gh api user --jq '.login'`)
- `reviewDecision` is empty or `REVIEW_REQUIRED` (no reviews submitted yet)

Exclude any PRs already captured in step 1 or step 2.

These go into a **Repo activity** section. This catches PRs on small teams where explicit review requests aren't always used.

If no unreviewed PRs from others exist, skip this section silently.

## Step 4: Query Jira

If the Atlassian MCP server is available (check for `mcp__atlassian__jira_search`), run two queries:

**Assigned to me:**
```
mcp__atlassian__jira_search with JQL: assignee = currentUser() AND status != Done ORDER BY updated DESC
```

**Contributor (custom field):**
```
mcp__atlassian__jira_search with JQL: cf[10466] = currentUser() AND status != Done ORDER BY updated DESC
```

Merge and deduplicate results by issue key (an issue can appear in both queries). Mark contributor-only issues with "(contributor)" so the user can distinguish ownership from involvement.

Show open Jira tickets under their own section with key, summary, status, priority, and project.

If `mcp__atlassian__jira_search` is not available, skip this step silently.

### Jira project to GitHub org mapping

When scoping results to the current repo, use this mapping to filter relevant Jira tickets:

| Jira project | GitHub org/repos |
|-|-|
| CONNLINK | Kuadrant/* (`kuadrant-operator`, `mcp-gateway`, etc.) |

If the current repo is in the Kuadrant org, include CONNLINK tickets. For repos not in this mapping, show all Jira tickets without org filtering.

## Step 5: Format output

Present results in markdown tables. Group by priority (highest first):

1. **Address feedback** -- my PRs where `reviewDecision` is `CHANGES_REQUESTED`. Invoke `clawdio:ship --resume` to fix.
2. **Review** -- PRs requesting my review. Open with `gh pr view <number>`.
3. **Merge** -- my PRs where `reviewDecision` is `APPROVED`. Merge with `gh pr merge <number> --squash`.
4. **My PRs** -- my open PRs where `reviewDecision` is `REVIEW_REQUIRED`
5. **Implement** -- GitHub issues assigned to me. Invoke `clawdio:ship #<number>` to start.
6. **Backlog** -- unassigned issues in this repo. Only shown when no issues are assigned to me. Invoke `clawdio:ship #<number>` to pick up, or `clawdio:pluck` to claim without implementing.
7. **Component owner** -- open PRs and unassigned issues in repos where I am an `OWNERS` approver/reviewer
8. **Repo activity** -- open PRs from others with no reviews yet
9. **Jira** -- open Jira tickets assigned to me

Skip sections with no results. Omit empty tables entirely.

Every table uses three columns. Build the first column as a markdown link from the `url` field returned by `gh`. Example row: `| [#30](https://github.com/org/repo/issues/30) | Title here | detail |`

For Jira tickets, build the link from the issue key: `| [PROJ-123](https://site.atlassian.net/browse/PROJ-123) | Title | status, priority |`

## Step 6: Recommend next action

Suggest what to tackle first. Offer to invoke `clawdio:ship` on the top item or open it with `gh issue view <number>` / `gh pr view <number>`.
