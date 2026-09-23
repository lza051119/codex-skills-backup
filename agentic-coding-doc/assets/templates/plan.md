# Plan

Use `plans/<sortable-time>-<topic>.md` at the repository root. A plan is a snapshot of working memory for one thread of work, written for whoever picks the thread up next — a compressed self, another agent, a human. Face forward: distill conclusions and the next step; do not transcribe the journey. Never authoritative — durable facts reconcile into `docs/` or code, and the thread's plans are deleted once landed.

```markdown
# Plan: {topic}

- Created: {date and time}
- Previous: {link to prior snapshot in this thread, or none — thread start}
- Thread state: exploring | building | verifying | blocked | landing

## TL;DR

{Three to five sentences: where this thread stands and what happens next.}

## Conversation recap

{Rounds since the previous snapshot — how intent evolved and what was decided. Compress ruthlessly: rounds that changed nothing merge into one row.}

| Round | User said | Intent behind it | Agent did | Outcome |
| --- | --- | --- | --- | --- |
| {Rn} | {summary} | {background} | {action} | {result} |

## Situation

{Current state relevant to this thread: what exists, what was recently landed, links to the exact docs/ records and code paths involved. Link, do not copy.}

## Open questions

{The problems this thread is working through. For each: the question, what has been tried or considered, current leaning and why. This is the section a future reader cannot re-derive.}

## Working conclusions

{Decisions reached so far and their rationale — pending reconciliation into docs/ or code. Note anything tried and abandoned, so it is not retried.}

## Progress and outlook

| Stage | Goal | Acceptance | Status | Commits |
| --- | --- | --- | --- | --- |
| {stage} | {target} | {observable condition} | done/active/planned | {SHAs or pending} |

## Next step

{The single concrete action the next reader takes to continue this thread.}
```

Granularity is the craft: too fine wastes the next reader's context; too coarse recovers nothing. The test — the thread resumes without re-derivation.
