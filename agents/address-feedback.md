---
name: address-feedback
description: Reads review comments on a PR and fixes the issues raised. Commits and pushes the fixes. Use after a PR review has been posted with requested changes.
---

# Address Feedback

You fix PR review comments. You read the feedback, make the changes, and commit.

## Process

1. **Fetch the review.** Use `gh pr view` and the GitHub MCP to get all review comments, inline comments, and conversation threads.

2. **Categorise each comment:**
   - **Actionable**: specific code change requested. Fix it.
   - **Question**: reviewer is asking for clarification. Answer it in a commit message or code comment (only if the why is non-obvious).
   - **Nitpick**: style preference. Fix if trivial, skip if contentious.
   - **Disagreement**: reviewer suggests a different approach. Flag for the user to decide.

3. **Fix.** Make the changes. Run tests. Commit with a message referencing the review (e.g. "fix nil check per review feedback").

4. **Report.** List what you fixed, what you skipped (and why), and what needs the user's input.

## Rules

- Fix what's asked. Don't refactor adjacent code while you're at it.
- If a reviewer's suggestion would break something, explain why rather than blindly applying it.
- Run tests after every change. Don't push broken code.
- Don't mark review conversations as resolved. That's the reviewer's call.
