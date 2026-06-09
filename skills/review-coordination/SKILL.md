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

Get the head commit SHA first:

```bash
COMMIT_SHA=$(gh api repos/{owner}/{repo}/pulls/{number} --jq '.head.sha')
```

Post via `gh api` with the reviews endpoint:

```bash
gh api repos/{owner}/{repo}/pulls/{number}/reviews --method POST --input - <<'EOF'
{
  "commit_id": "<commit_sha>",
  "event": "REQUEST_CHANGES",
  "body": "## Review verdict: CHANGES REQUESTED\n\n### Blockers\n- ...\n\n### Should fix\n- ...\n\n(plus any findings that reference lines outside the diff)",
  "comments": [
    {
      "path": "internal/broker/broker.go",
      "line": 42,
      "body": "**Critical:** unchecked nil dereference on error path"
    }
  ]
}
EOF
```

Rules:
- `event`: `"REQUEST_CHANGES"` when verdict is CHANGES REQUESTED or BLOCKED. `"COMMENT"` when APPROVE.
- `body`: the verdict summary (blockers, should-fix, nits) plus any findings that reference lines NOT in the diff. GitHub rejects inline comments on lines outside the diff, so those go here.
- `comments`: array of inline findings. Each needs `path`, `line` (line number in the NEW file from the diff hunk headers), and `body`.
- `commit_id`: the head SHA fetched above. Required.

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
