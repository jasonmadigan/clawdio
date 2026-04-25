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

Don't include:
- Implementation details the reviewer can see in the code
- Boilerplate sections with no content ("N/A", "None")
- AI-generated summaries of every file changed
