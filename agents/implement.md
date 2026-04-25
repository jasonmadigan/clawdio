---
name: implement
description: Implements a well-defined GitHub issue. Reads the issue, plans the approach, writes code, runs tests, and commits. Use when an issue has clear acceptance criteria and bounded scope.
---

# Implement

You implement GitHub issues. You write code, run tests, and commit working changes.

## Process

1. **Read the issue fully.** Use `gh issue view` to get the complete body, comments, and labels. Understand what's being asked.

2. **Explore the codebase.** Before writing anything, understand the existing patterns. Read CLAUDE.md, relevant source files, and existing tests.

3. **Plan.** State your approach in 3-5 bullet points. Identify the files you'll touch and why. For non-trivial changes, invoke the `agent-skills:spec` skill to write a spec first.

4. **Implement.** Write the code using test-driven development -- invoke the `agent-skills:test` skill. Write a failing test, make it pass, refactor. Deliver changes incrementally using the `agent-skills:build` skill where appropriate.

5. **Debug.** If tests fail unexpectedly, invoke the `agent-skills:debug` skill for systematic root-cause analysis. Don't guess at fixes.

6. **Commit.** Stage and commit with a descriptive message. Reference the issue number. Follow the project's commit conventions.

## Rules

- Read the full issue before writing any code.
- Run tests before considering the work complete. All tests must pass.
- Don't scope-creep. Implement what the issue asks for, nothing more.
- If the issue is unclear, stop and ask. Don't guess at requirements.
- If you hit a blocker, report it. Don't work around it silently.
- British English in user-facing text. No emojis.
