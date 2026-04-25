---
description: Scans GitHub for actionable work in the current repo. Shows issues assigned to you, PRs needing review, your open PRs and their status. Use when the user asks "what's on?", "what should I work on?", or "what next?".
---

# What Next

Find actionable work for the current repo.

## Process

1. Run the formatter script to get a consistent, pre-formatted output:

```bash
python3 "$(dirname "$(find ~/.claude/plugins/cache/jasonmadigan-workbench -name format.py -path '*/what-next/*' 2>/dev/null | head -1)")/format.py"
```

If the script is not found, fall back to running the queries manually (see below).

2. Present the script output verbatim. Do not reformat it. The script produces markdown tables with clickable links.

3. After the output, suggest what to do first based on priority:
   - Address feedback (unblock others) > Reviews requested (unblock others) > Approved PRs (merge and close) > My PRs awaiting review > Implementation (new work)

4. Offer to pull up the top item.

If the user says "what's on everywhere" or "across all repos", do not use the script. Run these queries manually instead:

```bash
gh search issues --assignee=@me --state=open --json number,title,labels,updatedAt,url --limit 20
gh search prs --review-requested=@me --state=open --json number,title,author,updatedAt,url --limit 20
gh search prs --author=@me --state=open --json number,title,updatedAt,url --limit 20
```

Format the results as markdown tables with the `url` field as a markdown link in the first column.
