# Information Architecture

Use this as `docs/product/ia.md` for products with a human-facing UI. It owns where behavior surfaces, never what the behavior is — Feature PRDs own behavior.

```markdown
# Information Architecture: {product-name}

- Status: draft | approved
- Owner: {owner}
- Human approval: {approver, date, exact Git identity, evidence, or pending}
- Last reconciled: {date}

## Surfaces

| Surface | Purpose | Primary user | Owning Features |
| --- | --- | --- | --- |
| {page/screen/panel} | {one line} | {persona} | {FEAT IDs} |

## Navigation

{Hierarchy or flow between surfaces: a tree or simple diagram. Include entry points and cross-surface transitions that the Feature PRDs cannot express.}

## UI vocabulary

| UI term | Glossary term | Note |
| --- | --- | --- |
| {label shown to users} | {Ubiquitous Language term it maps to} | {only when non-obvious} |
```

Keep it navigational. Do not restate Feature behavior, requirements, or acceptance criteria here; link the owning Feature PRD instead.
