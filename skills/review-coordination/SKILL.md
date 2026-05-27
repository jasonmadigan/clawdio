---
name: review-coordination
description: Coordinates multi-specialist PR review. Invoked by the router when a PR needs review.
---

# Review Coordination

Coordinates multi-specialist PR review. Invoked by the router when a PR needs review.

Subagents cannot spawn their own subagents. The router owns the review fanout.

## Step 1: Classify the PR

Fetch the file list (NOT the diff, NOT the code):

```bash
gh pr view <number> --json files --jq '[.files[].path]'
```

Determine which specialists are needed:

```
Files in PR
├── *.go, controllers/, api/, internal/ → dispatch go-k8s-reviewer
├── *auth*, *oauth*, *oidc*, *token*, *policy* → dispatch auth-reviewer
├── *crypto*, *secret*, *key*, *.env*, *password* → dispatch security-auditor
└── Always → dispatch code-reviewer + test-verifier
```

**Non-negotiable:** code-reviewer AND test-verifier are ALWAYS dispatched. No exceptions for "trivial" changes, single-file PRs, config-only PRs, or documentation PRs. The test-verifier decides whether tests are needed, not the router. If you find yourself thinking "this is too simple for test verification", that is the exact moment you must dispatch test-verifier.

**Skip domain specialists only when ALL of these are true:**
- The diff is under 50 lines
- 2 files or fewer changed
- No files touch auth, payments, data access, secrets, or config/env

When all three hold, dispatch code-reviewer + test-verifier only. Otherwise, classify files and dispatch domain specialists as normal.

## Step 2: Dispatch in parallel

Spawn ALL needed specialists simultaneously using the Agent tool. Pass each one:
- The PR number
- The full file list
- Instructions to read the diff via `gh pr diff <number>` and the PR description via `gh pr view <number>`

Example: for a Go PR with auth changes, dispatch four agents in parallel:
- code-reviewer
- test-verifier
- go-k8s-reviewer
- auth-reviewer

## Step 3: Collect, merge, and decide

When all specialists return, synthesise their findings into a single assessment. Do NOT just list reports -- merge them across these axes:

1. **Code quality** -- aggregate Critical/Important findings from code-reviewer and domain specialists. Resolve duplicates.
2. **Test coverage** -- pull from test-verifier. Flag gaps in acceptance criteria coverage.
3. **Security** -- promote any Critical findings from security-auditor (if dispatched) to blockers.
4. **Performance** -- pull from code-reviewer's performance findings or domain specialists.

Then produce a verdict:

```
## Review verdict: APPROVE | CHANGES REQUESTED | BLOCKED

### Blockers (must fix)
- [specialist: finding + file:line]

### Should fix
- [specialist: finding + file:line]

### Nits (author's call)
- [specialist: finding]
```

If any specialist returned a Critical finding, the default verdict is CHANGES REQUESTED.

## Step 4: Post to GitHub

Present the draft to the user. Follow the comment style from CLAUDE.md: terse, no preamble, no sign-offs, severity labels with file:line refs. Start with the verdict, then findings. Nothing else.

**MUST use `AskUserQuestion` tool** to present the draft. Options: "Post as-is", "Edit first", "Don't post". Do NOT ask "Want me to post this?" as plain text. Do NOT post without explicit approval via the tool. The user clicks an option, not types a response.

Once approved, post using the protocol below.

### Posting review findings

**BEFORE posting: confirm you are using `pull_request_review_write`, NOT `gh pr comment`. If you are about to use `gh pr comment`, STOP -- that posts a single wall of text instead of line-level comments.**

Findings that reference specific files and lines MUST be posted as review comments on those lines, not as a general PR comment. Use the GitHub MCP `pull_request_review_write` tool to create a review, and `add_comment_to_pending_review` for each line-level finding.

```
Posting flow:
├── Create a pending review: pull_request_review_write(method: "create", ...)
├── For each finding with a file:line reference:
│   └── add_comment_to_pending_review(path: "<file>", line: <line>, body: "<finding>", subjectType: "LINE")
├── For findings without a specific line (general observations):
│   └── Include in the review body, not as line comments
└── Submit the review: pull_request_review_write(method: "submit_pending", event: "COMMENT" or "REQUEST_CHANGES")
```

Use `event: "REQUEST_CHANGES"` when the verdict is CHANGES REQUESTED or BLOCKED. Use `event: "COMMENT"` when the verdict is APPROVE (submit the review as informational, not blocking).

The verdict summary (blockers, should-fix, nits) goes in the review body. Individual findings go as line comments. This puts feedback exactly where the author needs to see it.

Only fall back to `gh pr comment` if the GitHub MCP server is unavailable. This is worse but functional.

## Step 5: Suggest next action

After posting, if the verdict is CHANGES REQUESTED or BLOCKED, offer next steps via `AskUserQuestion`:

- "Address the feedback" → dispatch the **address-feedback** agent (NOT the router -- the router never fixes code)
- "Merge anyway" → invoke Skill(clawdio:merge-gate)
- "Done for now" → stop

If the verdict is APPROVE, offer:
- "Merge" → invoke Skill(clawdio:merge-gate)
- "Done for now" → stop

The address-feedback agent reads the review comments, categorises them, fixes what it can, and reports what needs your input. The router NEVER addresses feedback itself.

## Step 6: After address-feedback completes

When the address-feedback agent finishes, offer next steps via `AskUserQuestion`:

- "Re-review" → run review coordination again (step 1) to verify the fixes
- "Merge" → invoke Skill(clawdio:merge-gate)
- "What's on" → invoke Skill(clawdio:next) to check for other work
