---
name: verify-findings
description: Adversarially verifies specialist findings before they are presented or posted. Use when review, address-feedback, or triage agents return claims.
---

# Verify Findings

Specialist findings are claims, not facts. Before any Critical or Important finding is presented to the user or posted, dispatch adversarial verifiers, one per file, tasked with refuting each finding. Nits pass through unverified: not worth the tokens.

Read `../../references/dispatch-rules.md` before dispatching.

Two hard rules up front:

- Dispatch the logical `verifier` agent through the active client adapter.
- Verification fanout runs at the router main-loop level only. Do not nest it inside another specialist.

## Step 1: Fan out verifiers

One verifier agent per file that carries Critical/Important findings, all in parallel. Split a file with more than five such findings into groups of at most five. Findings on one file share its diff and surrounding code, so one fresh context reads them once. Never mix files in one verifier.

Each verifier prompt includes:

- Each finding verbatim with a short ID: severity, file:line, the claim, the suggested fix
- The repo and PR number (or the diff context if there is no PR)
- The instruction to REFUTE each finding independently, not to confirm it

For address-feedback claims, each finding to refute is "this fix addresses comment X", grouped by the file the fix touches; the verifier checks the diff actually resolves what each comment asked. For triage claims, one verifier takes the whole triage assessment (scope, reproducibility, labels).

## Step 2: Collect verdicts

| Verdict | Meaning | Handling |
|-|-|-|
| confirmed | Evidence the issue is real | Proceeds to presentation/posting |
| plausible | Could not refute, could not fully confirm | Proceeds to presentation/posting |
| refuted | Evidence it is wrong: unreachable path, existing guard or handling elsewhere, misread code, claimed line absent from diff | Filtered out, shown collapsed |

Line check: every verifier validates the finding's file:line against `gh api repos/{owner}/{repo}/pulls/{n}/files`. A finding whose line number cannot be verified is downgraded to a file + code snippet reference before posting -- never posted with a bad line number.

## Step 3: Output

Confirmed and plausible findings proceed unchanged. Refuted findings are never silently dropped -- they appear collapsed at the end of the report, one-line refutation each, so the filtering is auditable:

```
<details>
<summary>Filtered out by verification (2)</summary>

- ~~Critical: nil dereference in broker.go:42 (code-reviewer)~~ -- refuted: guarded by the err check at broker.go:38
- ~~Important: missing input validation in api.go:105 (security-auditor)~~ -- refuted: validated upstream in middleware.go:57
</details>
```

## Re-review rounds

Record refuted findings in the prior-review context that review-coordination Step 1.9 passes to specialists on round 2+, with the instruction not to re-raise them. Refuted findings do not resurrect.

## Anti-patterns

| Problem | Fix |
|-|-|
| Verifying Nits | Critical/Important only. Nits pass through. |
| Mixing files in one verifier, or more than five findings | One file per verifier, at most five findings, each judged on its own evidence. |
| Silently dropping refuted findings | Show them collapsed with refutations. Always auditable. |
| Skipping verification because findings "look obviously right" | Obvious findings slip through. Always verify Critical/Important. |
| Running the fanout inside a subagent | Router main loop only. |
| Using verifiers to audit an implementer's report, re-run its build, or check a whole branch | Verifiers refute specific findings. Review a change through `clawdio:review-coordination`. |
| Posting a finding with an unverified line number | Downgrade to file + snippet reference. |
| Bypassing the active client adapter | Follow `references/dispatch-rules.md`. |
