# Review Style

How specialist reviewers return findings, and how those findings read to the
author of a pull request. Applies to code-reviewer, security-auditor,
go-k8s-reviewer, auth-reviewer, and any other agent that produces review
findings. Each specialist's own file carries the domain it must not lecture on.

## Returning findings

Return enough evidence for the coordinator to verify each finding: severity,
file, line, the concrete failure mode, and a practical suggestion. Severity
labels stay in the internal result unless the reviewed repository's own
instructions require them in posted comments.

## Author-facing wording

- Lead with the concrete failure mode: the attack, the interoperability break,
  the panic, the wrong reconcile outcome. Not the category it belongs to.
- Then offer a practical suggestion, usually as "Could we ...?" where the
  implementation choice belongs to the author.
- Do not teach the language, the protocol, or the platform.
- Do not prescribe one implementation when several are valid.
- Do not overstate uncertain impact or uncertain conclusions.
- Describe what the code does only where that is needed to make the failure
  mode clear.

## Excluded from author-facing output

Nit and Low-severity findings, unless the user asked for them. They stay in the
internal result either way.
