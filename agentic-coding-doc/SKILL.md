---
name: agentic-coding-doc
description: A repository is a file system. docs/ maps the target; code is the territory; plans/ holds the working memory of the crossing between them. Every agentic operation reads from the map and writes to the territory. Use for any repository-level work — product, architecture, implementation, verification, decision-making. This skill defines the file-system conventions that make a repository navigable and self-describing without chat history, plus the platform conventions for PRs, issues, and comments. It prescribes no roles, no handoffs, and no dispatch protocol; agents decide how to organize their own work.
---

# Agentic Coding Doc

A repository is a file system with three planes. Code is the **territory** — the single authority for current state: what IS true. `docs/` is the **map** — target state and evidence: what SHOULD be true. `plans/` is the **crossing** — externalized working memory for the passage from territory toward map: what is happening right now. The planes answer different questions and never conflict; when a plan disagrees with map or territory, the plan is stale.

Every agentic operation — product scoping, architecture design, implementation, verification, decision-making — is a file-system edit: think in context, note the distillate to disk, iterate. Read the relevant index, locate the target, modify code and docs in one atomic unit, and leave the map truthful for the next agent. There is no protocol for who does what or in what order. Coordination has two surfaces: the file system itself, through its conventions — the durable one — and the code platform (PRs, issues, comments), which carries runtime work records. docs/ stays the single authority for facts; the platform never overrides the map.

Three rules follow from this:

1. **Scan the full map before acting.** Run `tree` on the stable domains (product/ + architecture/, full depth), shallow on growth domains (decisions/ testing/ resources/ references/ `-L 1`), and on `plans/` — an in-flight thread there may already hold the context this work needs. Every agent starts from the same global view; what differs is where the agent goes next, not whether it scans.

2. **Read the index before the leaf.** `docs/README.md` is the L0 router — it states the approved target, the current candidate, and the next decision. Every L1 directory README is a table of contents (ID | summary | state | read when | path). An agent that reads a leaf without navigating through its parent index is reading without knowing what else was relevant.

3. **This file is the single entry point.** The cold-start procedure, the mandatory skeleton, the routing conventions, and the naming rules are here. The companion `references/` directory (the documentation protocol and migration guide) is conditional: open it to establish or restructure documentation, to migrate a legacy repository, or to produce a canonical record — never as a prerequisite to start working.

## Working on Code

**Environment isolation.** Multiple coding agents run in parallel on the same machine; the shared checkout must never see concurrent edits or half-finished state. Every change that touches code starts on its own branch, in its own worktree.

**Local first.** Code agents are many — pushing every branch and worktree to origin creates chaos. Keep branches and worktrees local until the work is ready to land.

**Start clean, end clean.** Agents forget under context compression; stale worktrees and branches left behind accumulate and pollute the environment the next agent must navigate. When work ends — merged or abandoned — remove the worktree and delete the branch, local and remote.

## Platform Collaboration

The code platform (Forgejo today; whatever platform comes next) is the second coordination surface. Use its three record kinds, and never let them drift from the map:

**PRs are crossing records.** Every landed work unit opens a PR; its description states what changes and why, and references the defect issue it addresses. `Fixes #N` is the closing verb and belongs only on the PR that completes the defect — every layer merged and the issue's final retest evidence posted and passing; the merge then auto-closes the issue. A PR that is one layer of a layered fix, or whose fix still awaits final retest, references `Refs #N` — the merge does not close. Layered fixes accumulate in the same issue (each layer PR leaves its `Refs` trace in a comment); the final layer PR switches to `Fixes #N`. An issue closed with pending layers or pending retest is a false closure — worse than an open one. The merge commit is the trace that links territory back to the map.

**Read every comment before every action.** Before reviewing, merging, rebasing, replying to, or otherwise acting on a PR — read all of it: Approvals, Change Requests, inline review comments, and comments by anyone else, human or bot. A verdict binds to the head it reviewed; a verdict on an old head says nothing about the new one. The most common coordination failure is acting on a PR without reading its latest comments.

**Issues are runtime records.** A defect is a runtime fact — a diagnosis of the territory — not a map fact. Record it as a platform issue; the PR that fixes it closes it. docs/ keeps the router and the mapping index, not the running ledger.

**Reconcile after merge.** When a PR lands, its durable outcome reconciles into docs/ in the same unit of work. The platform record is the crossing trace; docs/ remains the authority.

## Repository Skeleton

### Standards

Five mature standards cover the documentation boundary. Only their composition in this file system is project-specific.

| Standard | Governs | In this repository |
| --- | --- | --- |
| **arc42** | `architecture/` | All 12 sections, one numbered file or directory per section. Four sections are routers to external authorities (see below). |
| **C4** | Diagrams inside arc42 files | C1 in `03-context-and-scope.md`; C2 in `05-building-block-view/README.md`; C3 in each container README. No Code level — the Code Map points to source. |
| **DDD** | `product/prd/` | One directory per Bounded Context; Feature = the smallest independently governed unit; the Master PRD Glossary is the Ubiquitous Language. Contexts relate through the catalog, never by nesting. |
| **BDD** | Acceptance criteria | Given-When-Then wherever a criterion is stated. |
| **MADR** | `decisions/` | One decision per file; accepted = frozen; superseded only by a new record. Any significant decision, not only architecture. |

Do not substitute project-specific synonyms for standard terms in canonical records; domain vocabulary lives in the PRD Glossary.

### Route Instead of Duplicating

Four arc42 sections overlap an external authority. They stay in place so the arc42 shape is complete, but they route instead of restating — each fact lives exactly once:

| Section | Single source | The section keeps |
| --- | --- | --- |
| `01-introduction-and-goals.md` | `product/` | Only the top architecture-driving quality goals; requirements are a pointer |
| `09-architecture-decisions.md` | `decisions/` | A one-paragraph router |
| `10-quality-requirements.md` | PRD cross-cutting requirements | Quality scenarios referencing PRD requirement IDs; no thresholds of its own |
| `12-glossary.md` | PRD Glossary | A one-paragraph router |

When two records seem to need the same fact, one of them links.

### Progressive Loading

Every agent follows the same navigation pattern:

1. Start at `docs/README.md` — the L0 router. It states the approved target, the current candidate, the material blocker, and the next move.
2. Follow the L1 indexes to the domain relevant to the goal. Each L1 README is a table (ID | summary | state | read when | path).
3. Read the leaf record. All detail lives at the leaf; indexes summarize and route, never duplicate.

The exact path depends on the goal, not on a role. For example, implementing a Feature starts at the roadmap → the owning Feature PRD → the architecture container. Verifying starts at the Feature PRD Traceability table → the relevant Test Report. Deciding starts at `decisions/README.md` → the relevant ADR. Exploring starts at the architecture README → the relevant section or container.

Every file change that alters a fact recorded in a parent index or a related record must update that record in the same atomic unit. A code change whose `docs/` consequence was not recorded is a context-breaking change.

### docs/

Every repository that follows this convention uses this fixed `docs/` tree:

```text
docs/
├── README.md                            ← L0: approved target, current candidate, next move
├── product/                             ← target behavior
│   ├── README.md                        ← Product Brief
│   ├── roadmap.md                       ← target priority sequence and rationale
│   ├── ia.md                            ← information architecture; UI products only
│   └── prd/
│       ├── README.md                    ← Master PRD: scope, cross-cutting requirements, Glossary
│       └── <context-name>/              ← one directory per Bounded Context; every Feature in exactly one
│           ├── README.md                ← context boundary + Feature catalog
│           └── feat-<context>-NNN-<name>.md ← Feature PRD: stories, requirements, BDD AC
├── architecture/                        ← target structure · arc42
│   ├── README.md                        ← L1: section index + Code Map
│   ├── 01-introduction-and-goals.md     ← architecture-driving quality goals; requirements live in product/
│   ├── 02-constraints.md
│   ├── 03-context-and-scope.md          ← system boundary, external actors and interfaces
│   ├── 04-solution-strategy.md          ← the few choices that shape everything, linked to ADRs
│   ├── 05-building-block-view/
│   │   ├── README.md                    ← every container: responsibility, communication matrix
│   │   └── <container-name>/            ← one directory per owned container
│   │       ├── README.md                ← container responsibility, interfaces, component index
│   │       └── <component-name>.md       ← one business-capability component
│   ├── 06-runtime-view/
│   │   ├── README.md                    ← scenario index
│   │   └── <scenario-name>.md           ← cross-container protocol, state machine, failure flow
│   ├── 07-deployment-view.md            ← topology and environment matrix; IaC lives in code
│   ├── 08-concepts/
│   │   ├── README.md                    ← concept index
│   │   └── <concept-name>.md            ← one cross-cutting rule set: security, observability, domain model…
│   ├── 09-architecture-decisions.md     ← router → ../decisions/
│   ├── 10-quality-requirements.md       ← quality scenarios; thresholds stay in PRD requirement IDs
│   ├── 11-risks-and-technical-debt.md
│   └── 12-glossary.md                   ← router → PRD Glossary
├── testing/                             ← independent verification records
│   ├── README.md                        ← verification strategy, acceptance surfaces, current verified candidate
│   └── defects.md                       ← defect router: mapping index → platform issues
├── decisions/                           ← decision records · MADR
│   ├── README.md                        ← ADR index
│   └── <adr-number>-<topic-name>.md     ← one decision per file; accepted = frozen
├── resources/                           ← governed external assets
│   └── README.md                        ← authorization, consumer, cost/quota, expiry, disposition
└── references/                          ← non-authoritative inputs
    └── README.md                        ← customer evidence, competitor scans, source annotation
```

These paths and index files are mandatory navigation, not optional documentation. Every project, of any size, creates every mandatory file — a small project is not small for an agent that cold-starts from files alone. Every directory carries a useful `README.md`. Write `none`, `pending`, or `not yet verified` when no fact exists yet; a missing file is indistinguishable from a forgotten one, a present file with a placeholder is a visible gap.

**Growth rule.** A numbered section is `NN-<name>.md` while it holds a single narrative, and becomes `NN-<name>/` — `README.md` carries the section body, one child file per enumerated unit — when independently loadable units accumulate. The number prefix never changes. §5, §6, and §8 enumerate by nature (containers, scenarios, concepts) and start as directories.

Every container you own gets a directory under `05-building-block-view/` with a README and one file per component; open-source containers (PostgreSQL, Redis, forgejo) are exempt.

Extend the skeleton only through indexed semantic units: Bounded Context directories and Feature PRDs; containers, scenarios, and concepts under their arc42 sections; decisions; governed resources; raw references.

### plans/

`plans/` sits at the repository root, beside `docs/` and the source tree. It is the crossing plane: externalized working memory for in-flight work — current thinking, open questions, what was tried, what comes next. Context is volatile, bounded, and private; a plan is the distillate that survives compression, session ends, and agent replacement.

Conventions that must converge across agents:

- **Path:** `plans/<sortable-time>-<topic>.md`, flat directory, one chain of snapshots per thread of work. Each plan links its predecessor; a snapshot covers only the increment since the last one.
- **Never authoritative.** A plan asserts no fact; when it disagrees with map or territory, the plan is stale. Durable outcomes reconcile into `docs/` or code, then the thread's plans are deleted — Git is the archive. An empty `plans/` is a visible fact: no crossing in flight.
- **Write at work boundaries, before context boundaries.** Snapshot before an implementation push and after it lands, when pausing, when context grows long — not after every exchange. After compression there is nothing left to distill.
- **Plan, not diary.** Granularity is the craft: too fine wastes context and cages the next reader; too coarse recovers nothing. The test — the next reader, whoever it is (a compressed self, another agent, a human), resumes the thread without re-deriving it. Face forward: conclusions-so-far and next step, not a transcript of the journey.

`docs/README.md` may link the newest plan as its next-move pointer.

## Naming

Two planes, one rule per plane. Never encode transient agent, thread, message, vendor, or worktree identities in either. See `references/documentation-protocol.md#naming` for the full catalog.

**Document IDs** — uppercase, stable, never recycled. Defined once and cross-referenced across files:

| Family | Format | Governs |
| --- | --- | --- |
| Feature | `FEAT-<CONTEXT>-NNN` | One independently governed product capability |
| User Story | `US-<CONTEXT>-NNN` | One user journey inside a Feature |
| Requirement | `REQ-<CONTEXT>-NNN` | One cross-cutting or Feature-scoped rule |
| Acceptance Criterion | `AC-<CONTEXT>-NNN` | One BDD acceptance condition |
| Architecture invariant | `ARC-INV-NNN` | One cross-cutting architectural constraint |
| Decision | `ADR-NNNN` | One accepted architectural or product decision |
| Defect | platform issue `#NNNN` (`DEF-NNN` stays as the issue-title prefix while a legacy ledger exists) | One recorded defect — a runtime fact, tracked as a platform issue |

**Filesystem paths** — lowercase kebab-case. Record types carry stable path patterns; name components carry semantic meaning, not transient identity.

## Templates

Templates in `assets/templates/` are starting points, not compliance checklists. Each captures the minimum structure that makes a record useful to the next agent. Do not delete a section because it does not apply — an absent section is indistinguishable from a forgotten one.

| Template | When to use |
| --- | --- |
| `product-brief.md` | A new product or a material change in product direction |
| `product-roadmap.md` | Every product; keep it current |
| `prd.md` | Every product; Master PRD + one Context PRD per Bounded Context + one Feature PRD per Feature |
| `ia.md` | Products with a human-facing UI |
| `architecture.md` | Every product; the full arc42 skeleton |
| `decision.md` | Any significant choice with meaningful alternatives and consequences |
| `test-report.md` | Every independent verification run; states the exact candidate tested, the procedures, the evidence, and the verdict |
| `plan.md` | A working-memory snapshot at each work boundary: before an implementation push, after it lands, when pausing, when context grows long |

A test report declares whether the author implemented the candidate. An independent verification carries more weight than implementation checks, but both are useful records.
