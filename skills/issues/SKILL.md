---
description: Create, update, and manage GitHub issues and their relationship to PRs. Use when creating issues, updating issue state, linking PRs to issues, or managing issue lifecycle. Replaces kdt:github-issues for clawdio workflows.
---

# Issues

Manage GitHub issues and their relationships to PRs throughout the SDLC lifecycle.

## Arguments

| Arg | Form | Example |
|-|-|-|
| action | positional | `issues create`, `issues update`, `issues close`, `issues link` |
| `--repo` | named | Override repo detection. Default: current repo |

## Creating issues

Use `gh issue create`. Always include:

```bash
gh issue create \
  --title "<imperative verb> <what>" \
  --body "$(cat <<'EOF'
## What

One paragraph. What needs to happen and why.

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2
EOF
)" \
  --assignee "@me"
```

Rules:
- Title is imperative, terse. "Add X" not "Adding X" or "X should be added".
- Body has two sections minimum: **What** and **Acceptance criteria**.
- Acceptance criteria are checkboxes. Each one is independently verifiable.
- Assign to the user unless they say otherwise.
- Add labels if the repo has them and they're relevant. Don't invent labels.

For multiple issues, create them sequentially and report a summary table:

```
| # | Title | URL |
|-|-|-|
| 10 | Add X | https://... |
| 11 | Fix Y | https://... |
```

## Updating issues

### State transitions

Use `gh issue edit` for metadata and `gh issue close`/`gh issue reopen` for state.

```bash
# add labels
gh issue edit <number> --add-label "in-progress"

# assign
gh issue edit <number> --add-assignee "@me"

# close with reason
gh issue close <number> --reason completed
gh issue close <number> --reason "not planned"

# reopen
gh issue reopen <number>

# update body
gh issue edit <number> --body "$(cat <<'EOF'
...
EOF
)"
```

### Lifecycle state map

Issues move through states based on what's happening in the workflow:

```
Issue created (open)
├── ship/implement dispatched → add "in-progress" label, assign to user
├── PR created linking issue → no change (still in-progress)
├── PR merged → close issue with --reason completed
├── PR closed without merge → remove "in-progress" label
├── blocked by diff gate → add comment explaining why, keep open
└── user manually closes → respect it, don't reopen
```

When other skills or agents reach lifecycle points, they should invoke this skill to keep issue state accurate:
- **ship phase 1 start**: assign issue, add "in-progress" label
- **ship phase 3 complete**: add comment with PR link
- **ship phase 5 complete**: close issue if PR was merged
- **worktree-worker blocked**: add comment with reason

## Linking PRs to issues

PRs link to issues via the PR body, not via issue comments. Use `Closes #N` or `Fixes #N` in the PR body.

```bash
# when creating a PR that addresses an issue
gh pr create --body "## Summary
...

Closes #42"
```

GitHub auto-closes the issue when the PR merges if the keyword is in the body. Supported keywords: `Closes`, `Fixes`, `Resolves`.

To check existing links:

```bash
# find PRs that reference an issue
gh pr list --search "42" --json number,title,url

# find issues linked from a PR
gh pr view <number> --json body --jq '.body' | grep -oE '(Closes|Fixes|Resolves) #[0-9]+'
```

## Querying issues

```bash
# list open issues
gh issue list --state open --json number,title,labels,assignees,url

# search with filters
gh issue list --label "bug" --assignee "@me" --state open

# get full issue detail
gh issue view <number> --json number,title,body,labels,assignees,state,comments
```

## Commenting on issues

Use comments to record workflow state changes, not for conversation. Keep them terse.

```bash
gh issue comment <number> --body "PR #<N> created. Implementation in progress."
gh issue comment <number> --body "Blocked: implement agent produced no changes. See diff gate."
```

Don't comment unless there's a state change worth recording. "Starting work" is not worth a comment. "Blocked because X" is.

## Bulk operations

When handling multiple issues (e.g. after parallel worktree dispatch):

```bash
# close multiple issues
for n in 10 11 12; do gh issue close "$n" --reason completed; done

# add label to multiple issues
for n in 10 11 12; do gh issue edit "$n" --add-label "in-progress"; done
```

## Issue-PR relationship queries

To understand the full picture of an issue:

```bash
# what PRs reference this issue?
gh pr list --search "<number>" --state all --json number,title,state,url

# is the issue's linked PR merged?
gh pr list --search "Closes #<number>" --state merged --json number,url

# what issues does this PR close?
gh pr view <number> --json body --jq '.body'
```

## Anti-patterns

| Problem | Fix |
|-|-|
| Creating issues without acceptance criteria | Always include checkboxes. Vague issues produce vague work. |
| Closing issues manually when a PR should do it | Use `Closes #N` in the PR body. GitHub handles it on merge. |
| Adding "in-progress" but never removing it | Remove the label if the PR is closed without merge or work is abandoned. |
| Commenting on every lifecycle step | Only comment on state changes that matter: blocked, PR created, reopened. |
| Creating duplicate issues | Search first: `gh issue list --search "<keywords>"` |
| Leaving issues open after PR merges | If `Closes #N` wasn't in the PR body, close manually after merge. |
| Updating issue state without checking current state | Read the issue first. Don't add "in-progress" if it's already there. |
