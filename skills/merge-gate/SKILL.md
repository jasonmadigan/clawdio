---
name: merge-gate
description: Pre-merge safety checks. Use when the router is preparing to merge a pull request.
---

# Merge Gate

Pre-merge safety checks. Invoked by the router before any merge.

Read `../../references/dispatch-rules.md` before loading another skill or
asking the user for a decision.

## Check tree

```
Merge request
├── Has the PR been reviewed?
│   ├── No → invoke clawdio:review-coordination first
│   └── Yes → continue
├── Are CI checks passing?
│   ├── No → report failures
│   └── Yes → continue
├── Is the branch behind base?
│   ├── Yes → offer to rebase first through the active user-decision mechanism
│   │         Options: "Rebase and merge", "Merge anyway", "Cancel"
│   │         Ours: gh pr update-branch, or `git rebase origin/main && git push --force-with-lease`
│   │         External: gh pr update-branch only, and only if maintainerCanModify
│   │                   Never rebase or force-push a contributor's branch
│   └── No → continue
├── Team repo?
│   ├── Yes → team member approved? → merge or flag
│   └── No → merge
└── Never use --admin or --force without explicit user instruction
```

## Check command

```bash
gh pr view <number> --json reviews,statusCheckRollup,reviewDecision,mergeable,mergeStateStatus,isCrossRepository,maintainerCanModify
```

`isCrossRepository: true` means the head branch is a fork. Merging it into a base repository we own is normal; writing to the head branch is not. See the PR provenance section of `../../references/dispatch-rules.md`.

`mergeStateStatus` values: `CLEAN` (good to go), `BEHIND` (needs rebase), `DIRTY` (conflicts), `BLOCKED` (checks failing or review missing). If `BEHIND` or `DIRTY`, do not merge without asking.

## Merge strategy

**Always use `--squash`** when merging: `gh pr merge <number> --squash --delete-branch`. Drop `--delete-branch` when `isCrossRepository` is true: the head branch lives in the contributor's fork and is not ours to delete. Do not use `--merge` or `--rebase` unless the user explicitly asks for a different strategy.

Merging and branch deletion are externally visible writes. Confirm both in the turn they happen, per `../../references/dispatch-rules.md`.

## Post-merge cleanup

After merging, if local branch deletion fails because a worktree still exists, clean up:

```bash
git worktree remove <worktree-path> --force 2>/dev/null
git worktree prune
git pull
```
