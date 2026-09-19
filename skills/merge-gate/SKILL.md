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
└── Never use --admin, --force or --force-with-lease without explicit user instruction
```

`--force-with-lease` is a force push. It refuses when the remote moved since
your last fetch, which is narrower than `--force`, but it still rewrites the
branch and is not a safe default. The only instruction that authorises the one
above is the user picking "Rebase and merge" at the `BEHIND` branch, and it
covers that push alone. On a contributor's branch there is no such option: see
the PR provenance section of `../../references/dispatch-rules.md`.

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

After merging, local branch deletion can fail because a worktree still holds
the branch. Remove only the worktree this workflow created for the branch that
was just merged. Resolve it from the branch rather than accepting a path:

```bash
BRANCH=$(gh pr view <number> --json headRefName --jq '.headRefName')
WT=$(git worktree list --porcelain | awk -v b="refs/heads/$BRANCH" '
  /^worktree /{p=substr($0,10)} /^branch /{if ($2==b) print p}')
```

Remove it only when both hold: `$WT` is non-empty, and `$WT/.clawdio-state`
exists, which is what marks the worktree as one clawdio created. Otherwise stop
and leave it alone -- a worktree without that file belongs to the user.

```bash
git -C "$WT" status --porcelain   # must print nothing
git worktree remove "$WT"
git worktree prune
git pull
```

Run `git worktree remove` without `--force` and without redirecting stderr. It
refuses on uncommitted or untracked files, and that refusal is the signal to
stop and tell the user which files are in the way. `--force` discards them with
no copy anywhere. Removing the worktree does not delete the branch, so commits
made in it survive.
