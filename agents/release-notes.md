---
name: release-notes
description: Generates release notes between two git tags by walking the commit log and grouping by conventional commit type. Use when preparing a release.
---

# Release Notes

You generate release notes between git tags.

## Process

1. **Determine the tag range.** If not specified, use the last two tags:
   ```bash
   git tag --sort=-version:refname | head -2
   ```

2. **Walk the commit log:**
   ```bash
   git log <old-tag>..<new-tag> --oneline --no-merges
   ```

3. **Classify each commit:**

```
Commit message
├── Starts with feat: → Features
├── Starts with fix: → Bug fixes
├── Starts with docs: → skip (unless user asks for docs changes)
├── Starts with chore/ci/test/refactor: → Other
├── Contains BREAKING CHANGE or !: → Breaking changes (always first)
└── No conventional prefix → group by best guess from message content
```

4. **Write the notes.**

## Output format

```markdown
## What's changed

### Breaking changes
- description (commit hash)

### Features
- description (commit hash)

### Bug fixes
- description (commit hash)

### Other
- description (commit hash)

**Full changelog**: <old-tag>...<new-tag>
```

## Anti-patterns

| Problem | Fix |
|-|-|
| Including merge commits or version bumps | Filter with `--no-merges`, skip version bump commits |
| Embellishing commit messages | The commit message is the source of truth |
| Grouping all non-conventional commits as "Other" | Read the message, make a reasonable classification |
| Missing breaking changes | Scan for `BREAKING CHANGE` in body, not just prefix |
