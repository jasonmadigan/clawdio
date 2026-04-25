---
name: release-notes
description: Generates release notes between two git tags by walking the commit log and grouping by conventional commit type. Use when preparing a release.
---

# Release Notes

You generate release notes between git tags.

## Process

1. Determine the tag range. If not specified, use the last two tags: `git tag --sort=-version:refname | head -2`.
2. Walk the commit log: `git log <old-tag>..<new-tag> --oneline`.
3. Group commits by conventional commit type (feat, fix, chore, docs, refactor, test, ci).
4. Write the release notes in the project's house style.
5. Include breaking changes prominently at the top.

## Output format

```markdown
## What's changed

### Breaking changes
- ...

### Features
- ...

### Bug fixes
- ...

### Other
- ...

**Full changelog**: <old-tag>...<new-tag>
```

## Rules

- Don't include merge commits or version bumps.
- Don't embellish. The commit message is the source of truth.
- If commits don't follow conventional commit format, group by best guess.
