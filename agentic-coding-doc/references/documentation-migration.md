# Documentation Migration

Migrate any nonconforming repository into the Documentation Protocol's canonical target state. Migrate facts, not filenames. Do not adapt the canonical skeleton to legacy layouts and do not preserve backward compatibility.

## Contents

- [Trigger and authority](#trigger-and-authority)
- [Inventory by fact](#inventory-by-fact)
- [Cut over](#cut-over)
- [Delete legacy structure](#delete-legacy-structure)
- [Verify](#verify)

## Trigger and authority

Start a documentation-migration project when any of these is true:

- a canonical top-level path is missing or a legacy alias exists;
- target, implementation, verification, Decision, or resource authority is duplicated or ambiguous;
- current facts exist only in chat, notes, historical records, or unindexed files;
- one giant document or spreadsheet prevents goal-scoped loading;
- a fresh agent cannot recover target, active work, exact candidate, evidence, resources, and next action from `docs/README.md`;
- links, stable IDs, or lifecycle cannot be determined.

Record the migration scope, exact baseline, write freeze, risks, and acceptance checks in a plan (`plans/<time>-migration.md`). All new documentation writes use canonical paths from that point onward.

## Inventory by fact

Inventory every current document and important undocumented fact. Do not infer authority from a legacy filename. Classify each item:

| Disposition | Use when |
| --- | --- |
| retain | Content and path already satisfy the canonical authority and loading contract |
| move | One authority is correct but the path is not canonical |
| merge | Multiple records duplicate one authority |
| split | One record mixes authorities, lifecycles, or independently loadable semantic units |
| extract | A durable fact must survive but its source record is process exhaust or non-authoritative input |
| delete | Content is stale, duplicated, derivable from code, superseded, or has no continuing evidentiary value |

Route facts into exactly one authority:

- product vision and users → Product Brief;
- target sequence → Roadmap;
- desired behavior, Bounded Contexts, Features, User Stories, Requirements, and Acceptance Criteria → the Master PRD, context PRDs, and Feature PRDs;
- intended system structure, runtime behavior, deployment topology, cross-cutting rules, quality scenarios, and technical risks → the owning arc42 section under `docs/architecture/`;
- intended external interfaces → `03-context-and-scope.md` with specs in code; inter-container interfaces → `05-building-block-view/`; protocols and observable state machines → `06-runtime-view/`;
- implementation reality → code, schemas, configuration, migrations, and artifacts; docs keep only locators;
- independent observations and verdicts → Test Reports and defect ledger;
- alternatives and consequences → Decision;
- governed external assets → resource record;
- raw, non-authoritative inputs → references.

Normalize a legacy feature spreadsheet into Bounded Context indexes, Feature PRDs, and Requirement rows. Keep the original only as a raw reference when provenance still matters; never retain it as a co-equal catalog.

Preserve stable requirement, Decision, defect, and evidence IDs when they are unambiguous. Resolve collisions explicitly in the migration project and repair every reference.

## Cut over

Migrate in this order so every later layer can link an established authority:

1. create and approve Product Brief, Roadmap, and Master PRD;
2. create Bounded Context indexes, normalize independently governed capabilities into Feature PRDs, and keep User Stories and atomic functions inside their owning Feature;
3. create the architecture section files, migrate durable target semantics into their owning arc42 sections, and replace current-state prose with a minimal Code Map;
4. reconcile current Test Reports, defects, exact candidate evidence, and test-code locators;
5. reconcile Decisions, resources, and non-authoritative references;
6. rebuild L0/L1 indexes bottom-up, then update `docs/README.md` last.

For each moved authority, freeze writes to its legacy source before the canonical version becomes writable. Never maintain both as co-equal sources.

## Delete legacy structure

After a canonical authority is verified:

- delete the legacy file or directory in the same migration;
- delete obsolete progress diaries, meeting transcripts, generated implementation narratives, duplicate schemas, and superseded intermediate Test Reports after extracting any durable fact;
- delete empty directories and unreferenced assets;
- rewrite inbound links instead of leaving redirect files;
- create no alias, mirror, compatibility shim, tombstone directory, or `archive/`;
- rely on Git history for recovery.

If an open defect, external audit, or human retention requirement still references an immutable record, keep that record at its canonical path until the retention trigger ends.

## Verify

The migration is incomplete until all checks pass:

1. `docs/` contains only the canonical top-level paths.
2. Every existing directory, including Bounded Context, container, and evidence directories, has a useful README and no empty directory remains.
3. Every current authoritative L2 record is reachable from `docs/README.md` through immediate-child indexes.
4. All relative links and stable IDs resolve uniquely.
5. Product target, implementation locator, and verified evidence remain distinct.
6. No prose claims implementation reality without pointing to exact code or artifact evidence.
7. No legacy path, alias, redirect, compatibility note, or duplicate authority remains.
8. All active work exposes exact baselines, current state, candidate, resources, blockers, and next action.
9. A fresh agent can locate the PRD, architecture constraints, code baseline, and required evidence without reading unrelated documents.
10. A fresh agent can identify the exact candidate, Acceptance Criteria, public black-box journeys, test system, and required inputs without reading implementation narration.
11. A fresh agent can recover the entire project state and make the next implementation, integration, scope, resource, or readiness decision without chat history.

Delete legacy structure and migration process exhaust before the final independent audit. Perform a cold-start audit against the post-cleanup tree. Record failures, repair them, and rerun every affected check. After all checks pass, close the migration project. Retain the completed project record and final Test Report while current evidence references them, then delete them under the normal lifecycle rules.
