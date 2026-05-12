---
name: pr-description
description: PR body template and conventions. Use when creating or reviewing a PR description to ensure it follows the team format.
---

# PR Description

Format the PR body when running `gh pr create`. Invoke via `clawdio:pr-description`. Every PR needs:

1. **Summary**: 1-3 bullet points. What changed and why.
2. **Linked issue**: `Closes #N` or `Relates to #N` (see `skills/issues/SKILL.md` for lifecycle).
3. **Test evidence**: what you ran (`go test ./...`, `npm test`, `make test`), what passed. If UI change, attach before/after screenshots.
4. **Breaking changes**: if any, call them out explicitly at the top.

Keep it short. Run `gh pr diff` to see what the reviewer sees; the description gives context the diff can't.

## Template

Use this when invoking `gh pr create --body`:

```markdown
## Summary

- <what changed and why>

## Test evidence

<command run, pass/fail>

Closes #<N>
```

## Checklist before submitting

Verify these before running `gh pr create`. If invoked from `skills/ship/SKILL.md`, the ship skill handles this automatically:

- [ ] Summary explains the why, not just the what
- [ ] Issue linked (`Closes #N` or `Relates to #N` in the body)
- [ ] Tests mentioned with pass/fail status
- [ ] Breaking changes called out (if any)
- [ ] No boilerplate sections with "N/A" or "None"
- [ ] Title follows imperative form ("Add X", not "Added X")

## Anti-patterns

| Problem | Fix |
|-|-|
| AI-generated summary of every file changed | The reviewer runs `gh pr diff`. Write the why, not the what. |
| "N/A" sections | Delete empty sections, don't fill them with placeholders |
| Implementation details the reviewer can see | Run `gh pr diff` to see what the reviewer sees. The PR explains the why. |
| No linked issue | Always link with `Closes #N`. If no issue exists, create one first via `clawdio:issues` |
| Title not imperative | Use "Add X" not "Adding X". Match `skills/issues/SKILL.md` title convention |
