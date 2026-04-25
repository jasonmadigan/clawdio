---
description: Scans GitHub for actionable work in the current repo. Shows issues assigned to you, PRs needing review, PRs with feedback to address. Use when the user asks "what's on?", "what should I work on?", or "what next?".
---

# What Next

Find actionable work for the current repo.

## Step 1: Run this script

Run this EXACTLY as written. Do not modify the commands or remove fields.

```bash
REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner') && echo "=== ISSUES ===" && gh search issues --assignee=@me --state=open --repo="$REPO" --json number,title,labels,updatedAt,url --limit 20 && echo "=== REVIEW REQUESTED ===" && gh search prs --review-requested=@me --state=open --repo="$REPO" --json number,title,author,updatedAt,url --limit 20 && echo "=== CHANGES REQUESTED ===" && gh search prs --author=@me --state=open --review=changes_requested --repo="$REPO" --json number,title,updatedAt,url --limit 20 && echo "=== APPROVED ===" && gh search prs --author=@me --state=open --review=approved --repo="$REPO" --json number,title,updatedAt,url --limit 20
```

If the user says "what's on everywhere" or "across all repos", remove `--repo="$REPO"` from each command.

## Step 2: Format the output

Group results by section. Use EXACTLY this format -- two lines per item, URL on the second line. The `url` field from the JSON results is the link. Do not use tables. Do not omit URLs.

Omit sections that returned empty results.

```
Implement (2)
  #30  Max cutout depth calculation                        2d ago
       https://github.com/tracefinity/tracefinity/issues/30
  #29  Cutout drag and drop behaviour with auto-size grid  2d ago
       https://github.com/tracefinity/tracefinity/issues/29

Review (1)
  #456  Add rate limit header support                      alice, 2h ago
        https://github.com/org/repo/pull/456
```

Include priority labels if present (P0, P1, priority/high, priority/critical).

## Step 3: Recommend

After the list, suggest what to do first. Priority order:
1. Address feedback (unblock others)
2. Reviews requested (unblock others)
3. Approved PRs (merge and close)
4. Implementation (new work)

Offer to pull up the top item.
