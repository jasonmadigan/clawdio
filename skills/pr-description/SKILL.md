---
description: PR body template and conventions. Use when creating or reviewing a PR description to ensure it follows the team format.
---

# PR Description

Every PR needs:

1. **Summary**: 1-3 bullet points. What changed and why.
2. **Linked issue**: `Closes #N` or `Relates to #N`.
3. **Test evidence**: what you ran, what passed. If UI change, before/after.
4. **Breaking changes**: if any, call them out explicitly at the top.

Keep it short. The diff tells the story; the description gives context the diff can't.

## Checklist before submitting

- [ ] Summary explains the why, not just the what
- [ ] Issue linked (Closes or Relates to)
- [ ] Tests mentioned with pass/fail status
- [ ] Breaking changes called out (if any)
- [ ] No boilerplate sections with "N/A" or "None"

## Anti-patterns

| Problem | Fix |
|-|-|
| AI-generated summary of every file changed | The reviewer can read the diff |
| "N/A" sections | Delete empty sections, don't fill them |
| Implementation details the reviewer can see | The code shows the what; the PR explains the why |
| No linked issue | Always link. If no issue exists, the PR description IS the spec. |
