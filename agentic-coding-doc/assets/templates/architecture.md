# Architecture

Templates for every record under `docs/architecture/` — the arc42 skeleton. Create the numbered section files when the project starts; create container, scenario, and concept files when their unit exists. Every file besides the router carries this metadata header:

```markdown
- Status: draft | approved
- Owner: {owner}
- Human approval: {approver, date, exact Git identity, evidence, or pending}
- Last reconciled: {date}
```

## `README.md` — section router and Code Map

```markdown
# Architecture: {product-name}

| Section | State | Read when |
| --- | --- | --- |
| [01 Introduction and goals](01-introduction-and-goals.md) | {state} | {condition} |
| … one row per section 01–12 … | | |

## Code Map

| Area | Responsibility | Implementation locator |
| --- | --- | --- |
| {area} | {one line} | {source directory, manifest, schema, migration, or symbol} |
```

## `01-introduction-and-goals.md`

```markdown
Requirements live in [`../product/`](../product/); this file keeps only what drives architecture.

| Quality goal | Motivating requirement | Architectural consequence |
| --- | --- | --- |
| {top 3–5 goals} | {REQ ID} | {what this forces} |

{Stakeholders only when they constrain architecture; otherwise omit.}
```

## `02-constraints.md`

```markdown
| Constraint | Source | Consequence |
| --- | --- | --- |
| {technical/organizational/regulatory} | {who or what imposes it} | {what it forbids or forces} |
```

A constraint is imposed from outside; a choice belongs in §4 or an ADR.

## `03-context-and-scope.md`

```markdown
{C1 diagram}

| External actor or system | Direction | What crosses the boundary | Interface |
| --- | --- | --- | --- |
| {actor} | in/out/both | {business content} | {spec locator in code, or protocol name} |

- Trust boundaries: {material boundaries or none}
- Out of scope: {explicitly outside the system}
```

## `04-solution-strategy.md`

```markdown
{The few fundamental choices that shape everything: decomposition principle, key
technology bets, how each §1 quality goal is achieved. One short paragraph or row
per choice; link the ADR that decided it.}

| Strategic choice | Achieves | Decided by |
| --- | --- | --- |
| {choice} | {quality goal or constraint} | {ADR link} |
```

## `05-building-block-view/README.md`

```markdown
{C2 diagram}

| Container | Target responsibility | Owns data | Technology | Detail |
| --- | --- | --- | --- | --- |
| {container} | {one cohesive responsibility} | {data or none} | {stack} | {directory link, or open-source: exempt} |

## Communication matrix

| From | To | Protocol | Sync/async | Interface semantics |
| --- | --- | --- | --- | --- |
| {container} | {container} | {protocol} | {mode} | {meaning and spec locator} |

- Permitted dependency direction: {rule}
```

## `05-building-block-view/<container-name>/README.md`

```markdown
# Container: {container-name}

- Target responsibility: {one cohesive responsibility}
- Exposed interfaces: {semantics and spec locators}
- Technology stack: {stack}
- Source: {repository/directory locators}

{C3 diagram when component relationships are non-obvious}

| Component | Target responsibility | Detail |
| --- | --- | --- |
| {component} | {one line} | {link} |
```

## `05-building-block-view/<container-name>/<component-name>.md`

```markdown
# Component: {component-name}

- Target responsibility: {one business capability}
- Owns: {behavior and data}
- Interface: {what collaborators may call or consume}
- Collaborators: {components or containers it depends on}
- Source: {directory or symbol locator}
```

Group components by business capability, never by technical layer.

## `06-runtime-view/README.md` and `<scenario-name>.md`

```markdown
# README: scenario index
| Scenario | Participants | Read when |
| --- | --- | --- |
| {link} | {containers} | {condition} |
```

```markdown
# Scenario: {scenario-name}

- Concern: {cross-container protocol, state machine, failure and recovery flow, or consistency mechanism}
- Participants: {containers and actors}

{Sequence or state diagram plus the target interaction; record only what no single
code location reveals — leave internal control flow to code.}

- Failure and recovery: {observable handling}
```

## `07-deployment-view.md`

```markdown
{Topology diagram or table per environment}

| Concern | dev | staging | production |
| --- | --- | --- | --- |
| {what differs} | {value} | {value} | {value} |

- Infrastructure requirements: {capacity, isolation, connectivity guardrails}
- IaC locators: {paths in code}
```

## `08-concepts/README.md` and `<concept-name>.md`

```markdown
# README: concept index
| Concept | Binds | Read when |
| --- | --- | --- |
| {link} | {containers or all} | {condition} |
```

```markdown
# Concept: {concept-name}

- Rule set: {cross-cutting concern governed here — domain model, security, multi-tenancy, observability, error handling…}
- Binds: {containers, data, deployment surfaces, or all}

{The target model, stated once.}

| ID | Invariant | Binds | Failure prevented |
| --- | --- | --- | --- |
| {ARC-INV-NNN} | {enforceable rule} | {scope} | {risk} |

| Surface | Enforcement or evidence locator |
| --- | --- |
| {surface} | {source/configuration/check locator or pending} |
```

## `09-architecture-decisions.md`

```markdown
Architecture decisions are recorded as ADRs in [`../decisions/`](../decisions/README.md).
```

## `10-quality-requirements.md`

```markdown
Thresholds live in PRD requirement IDs; this file elaborates them into scenarios and states none of its own.

| Scenario | Stimulus | Expected response | Owning requirement |
| --- | --- | --- | --- |
| {quality scenario} | {event/load/failure} | {observable response} | {REQ ID} |
```

## `11-risks-and-technical-debt.md`

```markdown
| Item | Impact | Trigger | Mitigation or acceptance rationale | Owner |
| --- | --- | --- | --- | --- |
| {risk or accepted debt} | {consequence} | {condition that realizes it} | {action or why accepted} | {owner} |
```

## `12-glossary.md`

```markdown
The vocabulary authority is the PRD Glossary: [`../product/prd/README.md#glossary`](../product/prd/README.md#glossary).
```

Mark a section that genuinely does not apply with one line of why; never delete the file or leave it empty. Machine-readable specifications stay in code and are referenced by exact identity, never mirrored as Markdown.
