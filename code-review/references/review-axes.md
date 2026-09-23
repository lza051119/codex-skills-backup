# Review axes and finding contract

Use this reference when assigning reviewers and validating findings.

## Authority / Spec / Scope

Check that the change implements the approved behavior, preserves repository-defined boundaries, updates the owner of every durable fact, and introduces no unsupported scope. Distinguish target-state documentation from current implementation and transient plans. Cite the exact authoritative rule; do not promote an issue, PR body, plan, or nearby code to authority without repository support.

## Correctness / Invariants

Trace success, empty, error, retry, cancellation, and boundary paths. Check state transitions, lifecycle ordering, idempotency, concurrency, resource ownership, cleanup, error propagation, and compatibility with callers. Prefer a reproducible input-to-failure chain over general concern.

## Contracts / Data / Compatibility

Check public APIs, protocol definitions, schemas, migrations, persisted data, generated artifacts, version negotiation, rollout order, and backward/forward compatibility. Verify all required projections remain synchronized. Treat generated output as evidence only after identifying its source-of-truth and generation rule.

## Security / Failure / Operations

Run this axis when risk-triggered. Check authentication, authorization, tenant boundaries, secret handling, injection, unsafe deserialization, path/network boundaries, fail-open behavior, rate/resource exhaustion, migration rollback, partial failure, retries, fencing, observability, recovery, and deployment/configuration safety. State the attacker, failure, or operational scenario; avoid generic security advice.

## Verification / Repository Standards

Check applicable repository instructions, focused tests, negative cases, contract/generation checks, lint/type/build gates, and whether evidence actually exercises the changed behavior. Report maintainability only when the diff creates a concrete defect risk or material maintenance burden. Repository rules override generic style preferences; skip matters already deterministically enforced unless the change disables or bypasses that enforcement.

## Finding format

Use one record per root cause:

```text
[P1] Short imperative title
Axis: Correctness / Invariants
Location: path/to/file.ext:<line at pinned head or worktree snapshot>
Authority/evidence: exact rule, contract, or execution path
Impact: concrete failing scenario and affected behavior
Direction: smallest useful correction, without implementing it
Confidence: high | medium
```

Do not report low-confidence speculation as a finding. Put genuinely unresolved questions under `Needs evidence`.

## Severity

- **P0 — critical:** immediate security, data-loss, or system-wide failure with no reasonable containment.
- **P1 — blocking:** reproducible correctness, contract, security, migration, or availability defect that should block merge.
- **P2 — material:** real defect or material regression with limited blast radius or a practical workaround.
- **P3 — minor:** localized maintainability or test weakness with a concrete future cost; never cosmetic preference.

Recommend `request changes` for any verified P0/P1. Use judgment for P2 based on repository policy and blast radius. `Approve` in the report means no verified blocking concern; publishing an approval remains a separate action.

## Reviewer prompt skeleton

Provide raw artifacts, not expected conclusions:

```text
Review only <axis> for the surface pinned by <manifest path>.
Applicable authorities: <exact paths/sections>.
Read the manifest, verify the relevant files still match it, and inspect necessary call sites.
Return candidate findings in the finding format plus coverage gaps.
Remain read-only. Do not fix, publish, approve, reject, or merge.
```
