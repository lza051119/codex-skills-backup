# Risk classes and evidence gates

Use the highest class triggered by any row. Risk is about blast radius and reversibility, not lines changed.

R0-R3 is this workflow's local change-risk scale, not an industry standard.

## Contents

- [Classification matrix](#classification-matrix)
- [R0 — non-behavioral](#r0--non-behavioral)
- [R1 — bounded local change](#r1--bounded-local-change)
- [R2 — contract or integration change](#r2--contract-or-integration-change)
- [R3 — critical authority or irreversible change](#r3--critical-authority-or-irreversible-change)
- [Modifiers](#modifiers)
- [TDD selection heuristic](#tdd-selection-heuristic)
- [Evidence reporting](#evidence-reporting)

## Classification matrix

| Dimension | R0 | R1 | R2 | R3 |
| --- | --- | --- | --- | --- |
| Runtime behavior | None | Bounded, reversible local or user-visible behavior | Shared/public compatibility commitment or multi-component behavior | Critical control path or broad production impact |
| Ownership | One document or mechanical file | One owned module/service | Multiple modules/services or consumers | Cross-owner authority or platform-wide invariant |
| Contracts | None | Private/internal only | API, Proto, event, CLI, config, compatibility surface | Identity, authorization, policy, trust, or irreversible contract |
| Persistent data | None | No schema/meaning change | Reversible schema evolution, backfill, cache/index semantics | Destructive/irreversible migration, tenant isolation, audit integrity |
| Security | None | No trust-boundary change | Input exposure, network/deployment policy, sensitive operational behavior | Authentication, authorization, secrets, tokens, grants, permissions, financial/compliance data |
| Concurrency/durability | None | Simple local state | Retry, ordering, idempotent consumer, distributed integration | Lease/fencing, exactly-once claims, durable ownership, race-sensitive authority |
| Operations | None | Easy local rollback | Rolling compatibility, dependency or deployment change | No proven rollback, outage risk, production-wide policy/resource change |
| Uncertainty | Mechanical and fully specified | Known pattern; local implementation choice | Ambiguity affects contract, ownership, rollback, or acceptance | Critical boundary has unclear failure/abuse behavior |

Examples are illustrative; classify from the actual consequences.

### R0 — non-behavioral

Typical: typo, prose, formatting, comment, dead-link repair, non-semantic rename in documentation.

Approval:

- A precise original instruction may count as approval.
- Ask only when the requested scope is ambiguous.

Minimum evidence:

- inspect the exact diff;
- run the applicable formatter, link check, or docs lint when required;
- prove no generated/runtime contract changed.

### R1 — bounded local change

Typical: isolated UI behavior, service-local pure logic, private refactor, reversible configuration with no external consumer.

Approval:

- present the change card;
- treat a precise original request as approval if discovery finds no material unresolved decision or path change;
- otherwise ask one concise approval question.

Minimum evidence:

- focused static/type/build/lint check for changed scope;
- focused unit or runtime check when behavior changed;
- inspect the diff for unintended scope;
- state rollback, usually revert.

Do not start multi-agent orchestration by default.

### R2 — contract or integration change

Typical: API/Proto/event evolution, database schema with rolling compatibility, cross-service flow, shared library, cache/index semantics, deployment/network change with bounded rollback.

Approval:

- grill one decision at a time;
- resolve owner, consumer impact, forward/backward compatibility, rollout, rollback, and acceptance;
- obtain explicit approval for the final path.

Minimum evidence:

- R1 evidence;
- evidence for every dimension that triggered R2:
  - contract change: source/generated consistency and affected-consumer compatibility;
  - ownership or component boundary: integration verification across that boundary;
  - data, deployment, or operations: rollout and rollback evidence;
  - externally visible behavior: the applicable negative or error path;
- independent Standards/Spec review;
- repository aggregate gate at its required boundary.

Prefer a dedicated worktree and explicit file/service ownership.

### R3 — critical authority or irreversible change

Typical: authentication, authorization, secrets, tokens, grants, audit, tenant isolation, destructive migration, financial/compliance behavior, session authority, lease/fencing, high-impact concurrency, production-wide policy, or absent rollback.

Approval:

1. Align intent, invariants, non-goals, and forbidden outcomes.
2. Challenge attack paths, failure modes, concurrency, recovery, migration, observability, and operational ownership.
3. Present the revised final card.
4. Obtain explicit final approval before Act.

Minimum evidence:

- R2 evidence;
- threat/abuse and fail-closed review;
- applicable negative authorization and tenant-isolation cases;
- applicable concurrency, retry, fencing, idempotency, crash/recovery, or replay evidence;
- migration rehearsal, backup/restore, or explicit proof that no data migration occurs;
- observability and operational rollback evidence;
- fresh-context independent security/failure review;
- full repository gate before PR/handoff;
- separate black-box or Candidate-bound verification when repository governance requires it.

Never treat user approval as permission to weaken mandatory safety, repository, or external-action constraints.

## Modifiers

- Classify uncertainty upward until read-only discovery resolves it.
- A tiny diff can be R3; a large generated-file update can be R1/R2.
- Generated artifacts take the risk of their source contract.
- A bug fix inherits the risk of the broken boundary.
- A refactor inherits the highest observable boundary it can affect.
- Tests alone do not lower risk. Evidence quality and rollback do.
- User urgency changes sequencing, not the class.

## TDD selection heuristic

Recommend test-first only when all are true:

1. The expected behavior can be stated before implementation.
2. A correct seam exercises the real behavior, not a mock-shaped approximation.
3. The test can fail for the target defect or missing capability.
4. The loop is faster than the plausible alternatives.

Usually skip test-first for visual layout, exploratory prototypes, mechanical configuration, glue code, generated output, or work whose correct seam does not yet exist. Still provide the evidence required by the risk class.

## Evidence reporting

Record exact commands and outcomes. Use:

- **passed** — command/procedure ran and supports the claim;
- **failed** — ran and found a problem;
- **not applicable** — the risk dimension is absent, with the factual reason;
- **not run** — intentionally omitted with reason;
- **blocked** — could not run because a named prerequisite is missing.

Do not convert `not applicable`, `not run`, or `blocked` into a pass. Distinguish implementation checks from independent or Candidate-bound verification.
