# Test Report

A Test Report is a frozen verification record — name the exact candidate, state the procedures, show the evidence, and issue a verdict. An independent report (author did not implement the candidate) carries more weight than implementation checks, but both are useful records.

```markdown
# Test Report: {scope}: {run-number}

- Author: {identity}
- Created: {date and time}
- Candidate verdict: PASS | FAIL | BLOCKED
- Supersedes or retests: {reports/defects or none}

## Independence

- Candidate implementers: {identities or unknown}
- Author did not implement the candidate: yes | no
- Candidate product code remained unchanged during verification: yes | no → BLOCKED
- Test-owned changes: {test/harness/fixture/environment paths or none}
- Test payload branches and commits: {map or none}

Test assets may be repaired during verification. A product defect stays in the report; the verifier never repairs the candidate it judges.

## Exact candidate

- Product repositories and originating SHAs: {map}
- Artifact identities: {map or none}
- Candidate provenance: {evidence the tested system comes from exactly these sources}
- PRD and Acceptance Criteria: {exact links and approved identity}

## Test system, environment, and resources

- Test system identity: {repository/commit, configuration, procedure version}
- Environment and data: {material runtime, services, sandbox, accounts, synthetic data}
- Governed test resources: {resource links or none; releasable now, still required with reason, or transferred}
- Durable evidence root: {path}

## Acceptance coverage

| Acceptance Criterion | Required? | Frozen applicability | Applicability evidence | Result | Durable evidence |
| --- | --- | --- | --- | --- | --- |
| {criterion-id} | {yes/no} | {condition} | {observation} | PASS | {evidence path or link} |

Use `PASS | FAIL | BLOCKED | N/A`; prove `N/A` from the frozen applicability condition. In a scoped retest, a carried-forward result names the prior report that proved it and the impact judgment that spares it.

## Functional black-box E2E

For every user-facing criterion, exercise the public interface and actual in-scope components as a human would. Automated scripts may drive the interaction but cannot replace this black-box journey.

| Journey and criteria | Public entry | Human-like actions | Real components traversed | Observed behavior | Visual and durable evidence |
| --- | --- | --- | --- | --- | --- |
| {journey; criterion IDs} | {UI/CLI/public API} | {click/type/upload/navigate/observe} | {application/services/storage/external sandbox} | {actual result} | {screenshots/recording/logs with paths} |

- Runtime-to-candidate proof: {evidence the exercised system serves the exact candidate}
- Synthetic account and data provenance: {details}
- Mocks, stubs, internal calls, or direct state mutation: {none, or why supplemental only}
- Irreversible external action sandbox: {authorized environment, or BLOCKED}
- User-facing journey omitted: {not applicable with product-contract evidence, otherwise BLOCKED}

## Other verification

| Layer | Exact command or procedure | Observed result | Durable evidence |
| --- | --- | --- | --- |
| {integration/system/regression/performance/security} | {procedure} | {observation} | {evidence path or link} |

## Findings and residual risk

| Defect | Severity | Defective surface | Affected criteria | Reproduction evidence | Next action |
| --- | --- | --- | --- | --- | --- |
| {defect-id} | {severity} | {product or test system} | {criteria} | {evidence} | {action and owner} |

- Blocked procedures and cause: {none or evidence}
- Regressions: {none or evidence}
- Untested or conditionally excluded surfaces: {reason and risk}
- Procedure deviations: {none or exact difference}

## Verdict rationale

{Explain why the evidence permits exactly this verdict. PASS requires an unchanged exact candidate, every required applicable criterion passing, and functional black-box E2E for every user-facing journey. A complete run may return FAIL. Any required procedure not executed returns BLOCKED while preserving completed evidence.}
```

Freeze this report on creation. Any material change to candidate, contract, test system, environment, or data requires a new run.
