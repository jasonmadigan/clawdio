#!/usr/bin/env python3
"""Formats what-next query results into consistent markdown tables."""

import json
import subprocess
import sys
from datetime import datetime, timezone


def age(ts):
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    delta = datetime.now(timezone.utc) - dt
    if delta.days > 0:
        return f"{delta.days}d ago"
    hours = delta.seconds // 3600
    if hours > 0:
        return f"{hours}h ago"
    return "just now"


def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        return []
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return []


def table(rows):
    if not rows:
        return ""
    lines = ["| # | Title | Detail |", "|-|-|-|"]
    lines.extend(rows)
    return "\n".join(lines)


def main():
    repo = subprocess.run(
        ["gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"],
        capture_output=True, text=True
    ).stdout.strip()

    if not repo:
        print("Not in a GitHub repo.")
        sys.exit(1)

    # my open PRs with review status
    my_prs = run(f'gh pr list --author @me --json number,title,updatedAt,url,reviewDecision --limit 20')

    feedback_rows = []
    merge_rows = []
    open_pr_rows = []

    for pr in my_prs:
        num, title, updated, url = pr["number"], pr["title"], age(pr["updatedAt"]), pr["url"]
        decision = pr.get("reviewDecision", "")
        if decision == "CHANGES_REQUESTED":
            feedback_rows.append(f"| [#{num}]({url}) | {title} | changes requested, {updated} |")
        elif decision == "APPROVED":
            merge_rows.append(f"| [#{num}]({url}) | {title} | approved, {updated} |")
        else:
            open_pr_rows.append(f"| [#{num}]({url}) | {title} | awaiting review, {updated} |")

    # PRs needing my review
    review_prs = run(f'gh search prs --review-requested=@me --state=open --repo="{repo}" --json number,title,author,updatedAt,url --limit 20')
    review_rows = []
    for pr in review_prs:
        num, title, updated, url = pr["number"], pr["title"], age(pr["updatedAt"]), pr["url"]
        author = pr.get("author", {}).get("login", "")
        review_rows.append(f"| [#{num}]({url}) | {title} | {author}, {updated} |")

    # issues assigned to me
    issues = run(f'gh search issues --assignee=@me --state=open --repo="{repo}" --json number,title,labels,updatedAt,url --limit 20')
    issue_rows = []
    for i in issues:
        num, title, updated, url = i["number"], i["title"], age(i["updatedAt"]), i["url"]
        labels = ", ".join(l["name"] for l in i.get("labels", []) if l["name"] not in ("triaged",))
        detail = f"{labels}, {updated}" if labels else updated
        issue_rows.append(f"| [#{num}]({url}) | {title} | {detail} |")

    # print sections in priority order
    sections = [
        ("Address feedback", feedback_rows),
        ("Review", review_rows),
        ("Merge", merge_rows),
        ("My PRs", open_pr_rows),
        ("Implement", issue_rows),
    ]

    output = []
    for name, rows in sections:
        if rows:
            output.append(f"**{name} ({len(rows)})**\n")
            output.append(table(rows))
            output.append("")

    if output:
        print("\n".join(output))
    else:
        print("Nothing actionable right now.")


if __name__ == "__main__":
    main()
