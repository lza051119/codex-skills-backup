# Helper-skill routing and conflict rules

Repository instructions and repository-owned authority always win over helper defaults. Reuse the method, not an incompatible filesystem or lifecycle.

## `grilling`

Use for unresolved user decisions.

- Ask one question at a time and include a recommendation.
- Discover facts from code, docs, and tools instead of asking.
- Make no behavior-changing edits before the applicable approval gate.
- Stop when the change card is complete and explicitly approved.
- Normally reserve relentless grilling for R2/R3; keep R0/R1 concise unless the user explicitly asks to be grilled.

## `grill-me`

Treat as a user-facing wrapper around `grilling`. The orchestrator normally invokes the underlying discipline directly.

## `grill-with-docs` and `domain-modeling`

Do not invoke automatically in a repository governed by `agentic-coding-doc`. Their default `CONTEXT.md` and `docs/adr` locations would create a second authority.

When terminology or a decision genuinely changes:

- route vocabulary to the repository's canonical glossary;
- route a material decision to the repository's decision authority and format;
- navigate through the repository's indexes first;
- ask before making documentation changes when they were not already in the approved scope.

Never create fallback files merely because a helper expects them.

## `prototype`

Use only to answer a named design question that source inspection cannot settle cheaply.

- Require approval before creating the prototype.
- State the question and deletion/retention plan.
- Keep it obviously throwaway and isolated from production behavior.
- Skip polish and tests unless the question itself requires them.
- Do not auto-commit, push, open an issue, or create an external pointer.
- Reconcile only the learned decision through repository-native authority, then remove or isolate the artifact as agreed.

## `diagnosing-bugs`

Use for hard bugs, intermittent failures, and performance regressions; do not force it onto a trivial, already-localized correction.

- Resolve vocabulary, architecture, and decisions through repository-native docs rather than assuming `CONTEXT.md` or a helper-specific ADR path.
- Build a tight red-capable feedback loop before theorizing.
- Run non-mutating source/log inspection and existing safe diagnostic commands without another approval gate. Obtain narrow approval before creating or editing reversible harnesses, tests, fixtures, or tagged instrumentation, then obtain separate fix approval after the root cause is known.
- Require a regression test only at a correct seam; record the absence of a seam rather than adding a misleading test.
- Keep temporary instrumentation uniquely tagged and remove it.
- Apply the normal R0-R3 class of the affected boundary.

## `code-review`

Use for R2/R3 or explicit review requests.

- Pass the exact candidate target, R0-R3 class, approved change card or repository-native authority manifest, and existing validation evidence.
- Let the helper resolve target semantics and produce a fingerprinted complete-surface manifest. Require committed, staged, unstaged, and safely scoped untracked coverage when each exists; never create a commit merely to satisfy review tooling.
- Require independent discovery followed by host verification, deduplication, and severity ordering. Repository authority overrides generic heuristics.
- For R3, or whenever security, concurrency, migration, recovery, authorization, or production-control boundaries are touched, require a fresh adversarial Security/Failure/Operations pass.
- Treat the returned findings as read-only evidence. Fixes, published PR comments, Approve/Request Changes, and durable defect records are separate actions with their own authority.
- If the helper is unavailable, reproduce this method with native subagents. Never install helper setup, run `setup-matt-pocock-skills`, or create `docs/agents/issue-tracker.md`.

## `handoff`

Use only when approved, incomplete work must continue in another session or agent context.

- In a governed repository, write the snapshot to the task's owning worktree and repository-native working-memory location, normally `plans/<sortable-time>-<topic>.md`; never default to Desktop or a global temp file.
- Record exact worktree, branch, PR, base/head fingerprints, observed dirty state, authority links, decision delta, invalidation conditions, one next action, and cleanup conditions. Link durable artifacts instead of copying them.
- Treat handoff as an ownership transfer. The receiving session validates the recorded state before acting; a mismatch invalidates the snapshot.
- Do not put credentials or environment dumps in a handoff. Do not let handoff authorize commit, push, merge, deploy, external publication, or worktree/branch cleanup.
- Do not create a handoff after completion. Reconcile durable facts, delete the thread's temporary snapshots according to repository rules, and report the finished outcome directly.

## Missing helpers

Do not install a missing helper automatically. Apply the equivalent discipline directly, or tell the user which optional helper would improve the workflow.

## Parallel agents

Use parallel agents only when independence is real:

- separate services/files with frozen shared contracts;
- competing read-only hypotheses;
- independent Standards, Spec, security, or verification reviews.

Give each implementation agent explicit ownership. Never let multiple agents edit the same files concurrently. The host agent integrates, verifies the actual diff, and owns the final report.
