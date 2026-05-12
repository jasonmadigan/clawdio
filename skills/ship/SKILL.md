---
name: ship
description: Full lifecycle skill for shipping an issue. Implements, pushes, creates PR, self-reviews, addresses issues, and prepares for merge. Use when the user says "ship this" or "ship #42".
---

# Ship

End-to-end lifecycle for shipping an issue to a merged PR.

## Arguments

Passed via the Skill tool's `args` string. Parse the following:

| Arg | Form | Example |
|-|-|-|
| issue ref | positional or `--issue` | `ship #42`, `ship --issue https://github.com/org/repo/issues/42` |
| `--resume` | flag | Resume an in-progress workflow from memory |
| `--skip-review` | flag | Skip the self-review phase |
| `--ready` | flag | Create PR as ready for review instead of draft |

If no issue ref is provided and no `--resume`, ask the user.

**Multiple issues:** if the user passes multiple issue refs ("ship #10, #11, #12"), do not handle this yourself. Tell `agents/router.md` to use parallel worktree dispatch via `agents/worktree-worker.md` instead. Ship handles one issue at a time.

## Resume

Before starting a new workflow, check for existing state:

1. Look for `memory/workflow_ship_*.md` files
2. If one exists for the current repo:
   - If `--resume` was passed, resume from the recorded phase
   - Otherwise, tell the user about the existing workflow and offer: "Resume from phase N" or "Start fresh"
3. If starting fresh with an existing state file, delete the old one first

## Process

### Phase 1: Implement

1. Update the issue state: assign to user and add "in-progress" label (per `clawdio:issues` lifecycle).
   ```bash
   gh issue edit <number> --add-assignee "@me" --add-label "in-progress"
   ```
2. Dispatch the implement agent on the issue. Wait for completion.

- [ ] All tests pass
- [ ] Implementation matches acceptance criteria
- [ ] No scope creep

**Diff gate:** verify the agent produced changes before proceeding.

```bash
COMMITS=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo "0")
CHANGES=$(git status --porcelain)
```

If `COMMITS` is 0 AND `CHANGES` is empty: STOP. Report "implementation produced no code changes -- the implement agent may have failed." Comment on the issue (per `clawdio:issues`), remove "in-progress" label, write state with `phase: blocked`. Do not proceed.

```bash
gh issue comment <number> --body "Blocked: implement agent produced no code changes."
gh issue edit <number> --remove-label "in-progress"
```

**Write state:** `phase: pre-ship`

### Phase 2: Pre-ship checks

2. Check if any files in `agents/`, `skills/`, or `hooks/` were changed:
   ```bash
   git diff --name-only origin/main..HEAD | grep -E '^(agents/|skills/|hooks/)'
   ```
   If matches found, invoke `clawdio:doc-sync` to verify and fix documentation.
3. Invoke `agent-skills:shipping-and-launch` for pre-ship checklist.
4. Invoke `agent-skills:git-workflow-and-versioning` for commit conventions.

- [ ] Docs are in sync (if agent/skill/hook files changed)
- [ ] Pre-ship checklist passes
- [ ] Commits follow conventions

**Write state:** `phase: reviewing`

### Phase 3: Self-review

Skip this phase if `--skip-review` was passed.

5. Review the changes locally before pushing. Tell the router to dispatch specialist reviewers (code-reviewer, test-verifier, and any domain specialists) against the local diff (`git diff origin/main..HEAD`).
6. If the review found real issues (Critical or Important), fix them. Commit.

- [ ] All Critical findings addressed
- [ ] All Important findings addressed
- [ ] Nits addressed if trivial, skipped if contentious

**Write state:** `phase: pushing`

### Phase 4: Push and PR

7. Create a branch if not already on one:
   ```bash
   git checkout -b <issue-number>-<short-description>
   ```
8. Push: `git push -u origin HEAD`
9. Create the PR via `gh pr create --draft` following the clawdio:pr-description skill format. Link the issue with `Closes #N` in the body. Draft is the default. Only omit `--draft` if `--ready` was passed.

- [ ] PR description follows template (summary, linked issue, test evidence)
- [ ] Branch name is descriptive (`<issue-number>-<short-description>`, not a system-generated name)
- [ ] PR is draft (unless --ready was explicitly passed)

**Write state:** `phase: ci-check`, include `pr: <url>`

### Phase 5: CI check

10. Check the status of CI checks on the PR:
    ```bash
    gh pr checks <number> --watch --fail-fast
    ```
    If `--watch` is available and checks are still running, this blocks until they complete. If `--watch` is not supported, poll with:
    ```bash
    gh pr view <number> --json statusCheckRollup --jq '[.statusCheckRollup[] | {name: .name, status: .status, conclusion: .conclusion}]'
    ```

11. If CI fails: report the failing checks, read the logs (`gh run view <run-id> --log-failed`), and offer to fix. Do not mark as ready for review.
12. If CI passes: report success. The PR is ready to be marked for review.
13. If CI is still running and has been for more than 5 minutes: report current status and tell the user to check back later or use `gh pr checks <number> --watch`.

- [ ] CI checks have completed
- [ ] All required checks pass
- [ ] If checks failed, failures reported with log excerpts

**Write state:** `phase: complete`

### Phase 6: Report

14. Tell the user: PR is ready for team review. Link to the PR. Include CI status.
15. Delete the state file from memory. Remove from MEMORY.md index.

## ## State file

Written after each phase gate. Path: `memory/workflow_ship_<branch>.md`

```markdown
---
name: workflow_ship_<branch>
description: Active ship workflow for <issue> on <branch>
type: project
---

- phase: implementing | pre-ship | pushing | reviewing | complete | blocked
- issue: <ref>
- branch: <name>
- pr: <url or pending>
- last-updated: <ISO date>
```

Add to `MEMORY.md` index when created. Remove from `MEMORY.md` on completion or when starting fresh.

## Decision tree: merge or wait?

```
PR ready
├── Personal repo + user said "ship and merge"?
│   └── Run `gh pr merge --squash`
├── Personal repo + user didn't say to merge?
│   └── Report PR link, let user decide
└── Team repo?
    └── Never merge automatically. Report PR link.
```

## Anti-patterns

| Problem | Fix |
|-|-|
| Merging on a team repo without asking | Never. The user decides after team review. |
| Skipping self-review | Always self-review unless `--skip-review`. Catches obvious issues before team sees them. |
| Pushing without running tests | Tests must pass before `git push`. |
| Creating a PR with a one-line description | Follow `skills/pr-description/SKILL.md` format. |
| Proceeding to push after implement produced nothing | Diff gate catches this. Check `git status --porcelain` before advancing. |
| Not checking for existing workflow state | Always check `memory/workflow_ship_*.md` for in-progress workflows before starting fresh. |
