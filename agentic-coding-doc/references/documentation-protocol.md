# Documentation Protocol

The canonical detail behind the Skill's `docs/` skeleton: what to create at initialization, which deeper records fire conditionally, what each contains, and how records are named and retired.

## Contents

- [Conditional paths](#conditional-paths)
- [Initialization](#initialization)
- [Progressive loading](#progressive-loading)
- [Root index](#root-index)
- [Product system](#product-system)
- [Architecture system](#architecture-system)
- [Test system](#test-system)
- [Lifecycle](#lifecycle)
- [Naming](#naming)
- [Cold start](#cold-start)

## Conditional paths

Create deeper records only when their semantic trigger fires:

```text
docs/product/ia.md                                        # product has a human-facing UI
docs/product/prd/<context-name>/README.md
docs/product/prd/<context-name>/feat-<context>-NNN-<name>.md

docs/architecture/05-building-block-view/<container-name>/README.md
docs/architecture/05-building-block-view/<container-name>/<component-name>.md
docs/architecture/06-runtime-view/<scenario-name>.md
docs/architecture/08-concepts/<concept-name>.md

docs/decisions/<adr-number>-<topic-name>.md
```

Bounded Contexts never nest: one level of context directories under `prd/`, related through the Master PRD catalog, never through subdirectories. Never place a User Story in its own file.

Apply the Skill's growth rule to architecture sections: a numbered section grows from `NN-<name>.md` to `NN-<name>/` (README.md carries the section body) when independently loadable units accumulate; the number prefix never changes.

Co-locate raw evidence in a report's `-evidence/` directory with a `README.md` manifest. Co-locate diagrams and assets with their owning document; do not create global asset taxonomies. Every created directory requires a useful `README.md`; never create an empty directory as a placeholder.

## Initialization

When starting from scratch — no existing code, no `docs/` — create every mandatory file in dependency order. Project size is irrelevant: a project judged "small" during initialization is one whose evidence surface cannot later be audited. Each layer links the one before it, so the root index is created last:

1. `docs/product/README.md`, `docs/product/roadmap.md`, `docs/product/prd/README.md`
2. `docs/architecture/README.md`, then every numbered file or directory — `01-` through `12-`, plus `05-building-block-view/README.md`, `06-runtime-view/README.md`, `08-concepts/README.md`
3. `docs/testing/README.md`, `docs/testing/defects.md`, `docs/decisions/README.md`, `docs/resources/README.md`, `docs/references/README.md`
4. `docs/README.md` — last; it links every path above

Write `none`, `pending`, or `not yet verified` when no fact exists yet. A missing file is indistinguishable from a forgotten one; a present file with a placeholder is a visible gap.

For a repository that already has code and documents but does not conform to this skeleton, follow [`documentation-migration.md`](documentation-migration.md) instead.

## Progressive loading

Apply the Skill's loading contract (tree → L0 → L1 → L2). Keep L0 near 300 words or less and each L1 index near 2,000 tokens or less unless semantic integrity requires more.

Every directory README index uses this minimum shape, adding evidence columns only where relevant:

| ID | One-line summary | State | Read when | Path |
| --- | --- | --- | --- | --- |
| `{stable-id}` | {what this child governs} | {state} | {condition} | {link} |

Apply these rules:

1. Keep L0 and every index node navigational. Summarize and link; do not copy normative leaf detail.
2. Split by Bounded Context and Feature, architecture section and unit, or lifecycle — not mechanically by heading or token count.
3. Split a file when it contains independently verifiable or evolving units, or when readers routinely need only part of it.
4. Keep one inseparable semantic unit intact even when long; length is a split signal, not the authority boundary.
5. Store each fact once. Summaries may lag while active work is in flight; reconcile before the next agent starts.
6. When an index approaches the loading budget, introduce a semantic child and move complete units under it; never paginate an authority as `part-1`, `part-2`, or a giant spreadsheet.

Use stable IDs plus repository-relative paths and Markdown anchors for deterministic addressing. Do not invent a URI scheme.

## Root index

Keep `docs/README.md` short. Link Product Brief, Roadmap, Master PRD, the architecture index, testing, decisions, resources, and references. State the approved target, exact current candidate or `not yet verified`, material blocker, and next move. Do not use it as a diary.

Every other directory README states its authority, current summary, direct-child index, and routing guidance. It is not a catch-all document.

When authorities disagree, record the mismatch and route it to the owner of the stale surface. Never resolve target-versus-code disagreement by rewriting history or treating prose as implementation proof.

## Product system

### Product Brief: `docs/product/README.md`

Maintain the stable Product vision, target users, problem and JTBD, value proposition, boundaries, non-goals, and success measures. Link Roadmap, Master PRD, and IA. Describe desired outcomes, never implementation internals.

### Roadmap: `docs/product/roadmap.md`

Maintain prioritized targets, value, dependency, intended scope, and activation condition. Roadmap states product intent, not live execution progress.

### Information architecture: `docs/product/ia.md`

Create only for products with a human-facing UI. Record the page inventory, navigation structure, and UI vocabulary mapped to Glossary terms. Do not restate Feature behavior — Feature PRDs own behavior; `ia.md` owns where behavior surfaces.

### PRD: `docs/product/prd/`

Treat the PRD as one logical document set with one canonical hierarchy: Bounded Context → Feature, with User Stories, Requirements, and Acceptance Criteria inside each Feature. Keep `prd/README.md` as the Master PRD: product scope, cross-cutting requirements, Glossary (the DDD Ubiquitous Language — the single vocabulary authority), and the Bounded Context catalog. Every Feature belongs to exactly one context.

Use each context `README.md` to define the context boundary, its local vocabulary that does not duplicate the Master Glossary, and its Feature catalog. Put each Feature's users, journeys, User Stories, functional and non-functional requirements, business rules, edge cases, scope, non-goals, Acceptance Criteria, and success measures in one Feature PRD.

A Feature is the smallest independently approved, planned, implemented, and accepted product capability; a button, endpoint, field, or validation rule is a Requirement inside a Feature, not another Feature. If a Story needs independent governance, promote it to a Feature with its own stable ID.

Do not use a spreadsheet or one giant Markdown table as product authority. Scale by context indexes and Feature PRD leaves; a generated spreadsheet may be a disposable view, never the canonical source.

At every PRD index level, keep target, implementation, and verification distinct:

| Feature ID | Summary | Product state | Implementation locator | Verified evidence | Detail |
| --- | --- | --- | --- | --- | --- |
| `{feature-id}` | {target} | proposed/approved/active/delivered/retired | {code path, symbol, commit, or pending} | {Test Report or not yet verified} | {link} |

An implementation locator is a navigation claim, not a substitute for reading code. A verification link proves only the exact candidate named by its Test Report.

## Architecture system

`docs/architecture/` is the arc42 template, one numbered file or directory per section. Mark a section that genuinely does not apply with one line of why; never delete the file or leave it empty — an absent section is indistinguishable from a forgotten one.

Machine-readable specifications (OpenAPI, AsyncAPI, Proto, JSON Schema, IaC) are build or runtime inputs and live with code; architecture files reference their exact identities and never mirror them as hand-maintained Markdown.

Per-section content contract:

- **`README.md`** — router only: a section index (section, one-line state, read-when) plus the Code Map (area, responsibility, source locator). No architecture content of its own.
- **`01-introduction-and-goals.md`** — the top 3–5 architecture-driving quality goals, each naming the PRD requirement that motivates it and the architectural consequence. Requirements overview is one pointer to `product/`. Stakeholders only when they constrain architecture.
- **`02-constraints.md`** — technical, organizational, and regulatory constraints as a table: constraint, source, consequence. A constraint is imposed from outside; a choice belongs in §4 or an ADR.
- **`03-context-and-scope.md`** — the system boundary: C1 diagram, external actors and systems, what crosses the boundary in business and technical terms, trust boundaries. External interface detail points to specs in code.
- **`04-solution-strategy.md`** — the few fundamental choices that shape everything: decomposition principle, key technology bets, how the §1 quality goals are achieved. Each strategic choice links the ADR that decided it.
- **`05-building-block-view/README.md`** — C2 diagram, the container inventory (container, responsibility, owned data, technology, detail link), the communication matrix (from, to, protocol, sync/async, interface semantics), and permitted dependency direction.
- **`05-building-block-view/<container-name>/README.md`** — the container's responsibility, exposed interfaces with semantics and spec locators, C3 diagram and component index, technology stack, and source locators.
- **`05-building-block-view/<container-name>/<component-name>.md`** — one business-capability component: responsibility, owned behavior and data, interface, collaborators, source locator. Never a technical layer.
- **`06-runtime-view/README.md`** — scenario index: scenario, participants, read-when.
- **`06-runtime-view/<scenario-name>.md`** — one runtime behavior that no single code location reveals: a cross-container protocol, state machine, failure and recovery flow, or consistency mechanism. Sequence and state diagrams belong here.
- **`07-deployment-view.md`** — deployment topology per environment, the environment matrix (what differs between dev, staging, production), infrastructure requirements, and IaC locators.
- **`08-concepts/README.md`** — concept index.
- **`08-concepts/<concept-name>.md`** — one cross-cutting rule set that binds multiple containers: domain model, security model, multi-tenancy, observability, error handling. State the model, its invariants (ID, rule, binds, failure prevented), and enforcement locators.
- **`09-architecture-decisions.md`** — one-paragraph router to `../decisions/`.
- **`10-quality-requirements.md`** — quality scenarios: stimulus, expected response, and the PRD requirement ID that owns every threshold. This file states no thresholds of its own.
- **`11-risks-and-technical-debt.md`** — known technical risks and accepted debt: item, impact, trigger, mitigation or acceptance rationale, owner.
- **`12-glossary.md`** — one-paragraph router to the PRD Glossary.

## Test system

Use `docs/testing/README.md` for verification strategy, test-code locators, and a report index. Executable tests remain code; document only verification policy and navigation not recoverable from test code.

Defects are runtime facts and live as platform issues: one issue per defect, carrying stable ID, affected criteria, severity, defective surface, disposition, fix identity, and retest evidence; the completing PR references it with `Fixes #N` so the merge closes it; layer PRs and pending-retest PRs reference `Refs #N` and do not close. `docs/testing/defects.md` is the frozen mapping index (DEF-NNN → issue number) that keeps legacy document links alive — add new defects as issues, not ledger rows.

Test Reports (template `test-report.md`) record exact procedures, environments, observations, verdicts, and evidence. An independent report — where the author did not implement the candidate — carries more weight than implementation checks, but both are useful records. Keep screenshots, recordings, and large outputs in the report's evidence directory and link them by stable path.

## Lifecycle

- **Living:** Product Brief, Roadmap, IA, PRD, architecture sections, and indexes. Update in place; Git preserves history. A material target or architecture change requires human reapproval.
- **Frozen:** Test Reports and Decisions. Amend through a superseding record.
- **Ephemeral:** Plans (`plans/` at the repository root, outside `docs/`) and intermediate artifacts. Delete when no longer referenced; Git is the archive.

Reconcile durable facts into their living authorities when a project closes. Do not create an archive directory.

## Naming

Two planes, one rule per plane. Never encode transient agent, thread, message, vendor, or worktree identities in either.

**Document IDs** — uppercase, stable, never recycled. Defined once and cross-referenced across files.

| Family | Format | Governs |
| --- | --- | --- |
| Feature | `FEAT-<CONTEXT>-NNN` | One independently governed product capability |
| User Story | `US-<CONTEXT>-NNN` | One user journey inside a Feature |
| Requirement | `REQ-<CONTEXT>-NNN` | One cross-cutting or Feature-scoped rule |
| Acceptance Criterion | `AC-<CONTEXT>-NNN` | One BDD acceptance condition |
| Architecture invariant | `ARC-INV-NNN` | One cross-cutting architectural constraint |
| Decision | `ADR-NNNN` | One accepted architectural or product decision |
| Defect | platform issue `#NNNN` (`DEF-NNN` stays as the issue-title prefix while a legacy ledger exists) | One recorded defect — a runtime fact, tracked as a platform issue |

`<CONTEXT>` is the Context's uppercase abbreviation — chosen once when the Context is created, recorded in the Master PRD Context catalog, and never changed. The abbreviation is not mechanically derived from the directory name; it is a deliberate short label (e.g. `PAY` for the payment context, not `PAYMENT-PROCESSING`).

**Filesystem paths** — lowercase kebab-case. Record types carry stable path patterns; name components carry semantic meaning, not transient identity.

| Record | Path pattern | Name component |
| --- | --- | --- |
| Context directory | `prd/<context-name>/` | `name` = lowercase context name |
| Feature PRD | `feat-<context-name>-NNN-<name>.md` | `name` = Feature name, kebab-case |
| Container directory | `05-building-block-view/<container-name>/` | `name` = container runtime name |
| Component file | `<component-name>.md` | `name` = business capability, kebab-case |
| Scenario file | `<scenario-name>.md` | `name` = scenario, kebab-case |
| Concept file | `<concept-name>.md` | `name` = cross-cutting rule set, kebab-case |
| Report file | `report-<task-name>-<run>.md` | `task-name` = task, kebab-case; `run` = sequential execution |
| Decision file | `<adr-number>-<topic-name>.md` | `adr-number` = ADR number; `topic-name` = kebab-case |

Add an ID family or a path pattern only when it eliminates real ambiguity.

## Cold start

Cold-start acceptance requires a fresh agent to identify, without chat history: why the Product exists; what target is approved; which architecture governs; what code to read; which exact candidate is verified; what evidence supports it; which resources remain; and what happens next.

Write target, decisions, state, evidence, and next action. Omit transcripts and repeated narration. Link exact code and raw artifacts instead of copying them. Evidence belongs only to its exact candidate.
