# PRD

Use the first template for `docs/product/prd/README.md`, the second for `docs/product/prd/<context>/README.md`, and the third for a Feature PRD at `docs/product/prd/<context>/feat-<context>-NNN-<name>.md`. The PRD is one indexed logical document set; never combine the templates into a monolith or create User Story files. Bounded Contexts never nest — one level of context directories, related through the Master catalog. Every product has at least one Context; every Feature belongs to exactly one.

## Master PRD

```markdown
# PRD: {product-name}

- Status: draft | approved
- Owner: {owner}
- Product Brief: {link}
- Roadmap: {link}
- Human approval: {approver, date, exact Git identity, evidence, or pending}
- Last reconciled: {date}

## Product scope

- Target: {observable complete target}
- In scope: {product boundary}
- Non-goals: {explicit exclusions}

## Cross-cutting requirements

{Only requirements that bind multiple Features: product-wide security, privacy, accessibility, reliability, performance, compatibility, cost, or operability. Assign stable IDs — these own every quality threshold; architecture §10 references them.}

## Glossary

| Term | Exact meaning |
| --- | --- |
| {domain term} | {definition; no synonym anywhere in canonical records} |

The Glossary is the Ubiquitous Language — the single vocabulary authority for the whole project.

## Bounded Context catalog

| Context | Abbreviation | Target summary | State | Read when | Context PRD |
| --- | --- | --- | --- | --- | --- |
| {context name} | {short uppercase; chosen once, never changed} | {one line} | proposed/approved/active/delivered/retired | {relevance condition} | {link} |

{Every product has at least one context; list them here.}
```

## Bounded Context PRD and Feature Catalog

```markdown
# Context: {context-name}

- Status: proposed | approved | active | delivered | retired
- Owner: {owner}
- Master PRD: {link}
- Human approval: {approver, date, exact Git identity, evidence, or pending}
- Last reconciled: {date}

## Boundary

- Target: {cohesive product capability owned by this context}
- In scope: {included capability}
- Non-goals: {excluded or elsewhere-owned capability}
- Local vocabulary: {terms local to this context that do not duplicate the Master Glossary, or none}

## Feature Catalog

| Feature ID | Target summary | Product state | Implementation locator | Verified evidence | Read when | Feature PRD |
| --- | --- | --- | --- | --- | --- | --- |
| {FEAT-CONTEXT-001} | {one line} | proposed/approved/active/delivered/retired | {code path, symbol, commit, or pending} | {Test Report or not yet verified} | {relevance condition} | {link} |
```

Keep this index navigational. When it cannot remain within the loading budget, split by Feature groups inside the catalog; never paginate it or replace it with a canonical spreadsheet.

## Feature PRD

```markdown
# {feature-id}: {feature-name}

- Status: proposed | approved | active | delivered | retired
- Owner: {owner}
- Bounded Context: {link, or Master PRD for flat layouts}
- Roadmap target: {link}
- Human approval: {approver, date, exact Git identity, evidence, or pending}
- Related Projects: {links or none}
- Last reconciled: {date}

## Problem, users, and target

- Problem and context: {who encounters what problem and why it matters}
- JTBD: {desired user progress}
- Target state: {observable Feature behavior after completion}

## User journeys and User Stories

### {US-CONTEXT-001}: {story title}

As {user}, I can {behavior} so that {value}.

- Entry state: {state}
- Journey: {human-observable actions and outcomes}
- Independent value: {what this Story delivers alone}
- Applicability: {conditions}

## Requirements and rules

| Requirement ID | Kind | Applies when | Required behavior | Failure or edge behavior |
| --- | --- | --- | --- | --- |
| {REQ-CONTEXT-001} | function/rule/quality/constraint | {condition} | {technology-agnostic observable requirement} | {boundary behavior} |

Include Feature-specific NFRs only when cross-cutting PRD requirements do not already govern them.

## Scope

- In scope: {behavior included}
- Non-goals: {explicit exclusions}
- Deferred: {later target or none}

## Acceptance Criteria

| Criterion ID | Required? | Applies when | Given-When-Then | Required evidence |
| --- | --- | --- | --- | --- |
| {AC-CONTEXT-001} | {yes/no} | {condition} | Given {state}, when {action}, then {observable behavior} | {black-box E2E, other Test evidence, or inspection} |

## Success measures

| Measure | Baseline | Target | Measurement and horizon |
| --- | --- | --- | --- |
| {outcome} | {value or unknown} | {value} | {method} |

## Traceability

| Target ID | Implementation locator | Integrated identity | Test Report | Verdict |
| --- | --- | --- | --- | --- |
| {US/REQ/AC ID} | {code path, symbol, commit, or pending} | {dev SHA or pending} | {link or not yet verified} | {PASS/FAIL/BLOCKED/N/A/pending} |

## Open questions

| Question | Owner | Decision path | Blocking? |
| --- | --- | --- | --- |
| {question} | {owner} | {human/Decision/Project} | yes/no |
```

Add further User Story sections inside the Feature PRD. If a Story requires independent approval, planning, implementation, acceptance, or lifecycle, promote it to a Feature instead of creating a Story file. Keep implementation locators navigational; code and artifacts remain implementation authority. Update the living PRD in place and use Git identities for approved target versions.
