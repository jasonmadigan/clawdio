---
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
| `--draft` | flag | Create PR as draft (skips the draft/ready prompt) |

If no issue ref is provided and no `--resume`, ask the user.

**Multiple issues:** if the user passes multiple issue refs ("ship #10, #11, #12"), do not handle this yourself. Tell the router to use parallel worktree dispatch instead. Ship handles one issue at a time.

## Resume

Before starting a new workflow, check for existing state:

1. Look for `workflow_ship_*.md` files in memory
2. If one exists for the current repo:
   - If `--resume` was passed, resume from the recorded phase
   - Otherwise, tell the user about the existing workflow and offer: "Resume from phase N" or "Start fresh"
3. If starting fresh with an existing state file, delete the old one first

## Process

### Phase 1: Implement

1. Dispatch the implement agent on the issue. Wait for completion.

- [ ] All tests pass
- [ ] Implementation matches acceptance criteria
- [ ] No scope creep

**Diff gate:** verify the agent produced changes before proceeding.

```bash
COMMITS=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo "0")
CHANGES=$(git status --porcelain)
```

If `COMMITS` is 0 AND `CHANGES` is empty: STOP. Report "implementation produced no code changes -- the implement agent may have failed." Write state with `phase: blocked`. Do not proceed.

**Write state:** `phase: pre-ship`

### Phase 2: Pre-ship checks

2. Invoke `agent-skills:shipping-and-launch` for pre-ship checklist.
3. Invoke `agent-skills:git-workflow-and-versioning` for commit conventions.

- [ ] Pre-ship checklist passes
- [ ] Commits follow conventions

**Write state:** `phase: pushing`

### Phase 3: Push and PR

4. Create a branch if not already on one:
   ```bash
   git checkout -b <issue-number>-<short-description>
   ```
5. Push: `git push -u origin HEAD`
6. Ask the user via `AskUserQuestion`: "Create as draft PR or ready for review?" with options "Draft PR" and "Ready for review".
7. Create the PR via `gh pr create` following the clawdio:pr-description skill format. Link the issue. If draft, add `--draft`.

- [ ] PR description follows template (summary, linked issue, test evidence)
- [ ] Branch name is descriptive
- [ ] Draft/ready matches user preference

**Write state:** `phase: reviewing`, include `pr: <url>`

### Phase 4: Self-review

Skip this phase if `--skip-review` was passed.

7. Tell the router to review the PR you just created. The router will dispatch specialist reviewers (code-reviewer, test-verifier, and any domain specialists) in parallel.
8. If the review found real issues (Critical or Important), fix them. Commit and push.

- [ ] All Critical findings addressed
- [ ] All Important findings addressed
- [ ] Nits addressed if trivial, skipped if contentious

**Write state:** `phase: complete`

### Phase 5: Report

9. Tell the user: PR is ready for team review. Link to the PR.
10. Delete the state file from memory. Remove from MEMORY.md index.

## State file

Written to memory after each phase gate. Path: `memory/workflow_ship_<branch>.md`

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

Add to `MEMORY.md` index when created. Remove on completion or when starting fresh.

## Decision tree: merge or wait?

```
PR ready
├── Personal repo + user said "ship and merge"?
│   └── Merge via gh pr merge --squash
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
| Pushing without running tests | Tests must pass before push. |
| Creating a PR with a one-line description | Follow the clawdio:pr-description skill format. |
| Proceeding to push after implement produced nothing | Diff gate catches this. Check git state before advancing. |
| Not checking for existing workflow state | Always check memory for in-progress workflows before starting fresh. |
