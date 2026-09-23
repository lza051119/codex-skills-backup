---
name: handoff
description: Transfer incomplete work safely between Codex sessions by creating or resuming a compact, verifiable handoff snapshot. Use when unfinished repository or non-repository work must cross a session boundary, especially with parallel sessions, or when validating an existing handoff before continuing. Do not use for ordinary status summaries or completed work.
---

# Handoff

Treat a handoff as an explicit ownership transfer, not as a transcript, lock, source of truth, or permission to mutate external state.

## Create a handoff

1. Confirm that approved work is incomplete and must move to another session. If the work is complete, create no handoff: follow the repository's normal completion process to reconcile durable facts into their authorities and remove obsolete plans when authorized.
2. For repository work, identify the **owning task worktree**. Write there, never in a shared checkout or on the Desktop by default. Create a unique snapshot at `plans/YYYY-MM-DD-HHmmss-<topic>-handoff.md`; set `Previous snapshot` to its immediate predecessor, and never overwrite history or maintain `CURRENT.md`.
3. For non-repository work, create the file in the operating system's temporary directory using a platform-native facility such as Python `tempfile` or PowerShell `New-TemporaryFile`. Do not assume a Unix-only command exists.
4. Copy [assets/repository-handoff.md](assets/repository-handoff.md) and replace every placeholder. Link to AGENTS files, product or architecture authorities, PRs, commits, reports, and prior plans instead of duplicating them.
5. Record the owning worktree, branch, PR, base/head SHAs, capture time, exact status, and a reproducible working-tree fingerprint covering staged, unstaged, and scoped untracked paths/contents. If no field applies, write `none` and why; do not treat a clean status as proof that no other session owns the worktree.
6. Record only the decision delta since the predecessor. Mark unreconciled decisions as provisional; never turn chat history or a handoff into authority.
7. Specify exactly one bounded next action plus concrete invalidation conditions and cleanup criteria.
8. Remove secrets and credential material, including tokens, cookies, authorization headers, passwords, private keys, DSNs with passwords, kubeconfigs, and environment dumps. Refer to the credential source by name or setup command, never its value.
9. Return the absolute snapshot path and tell the receiving session to validate it before acting. After transfer, the sending session must stop mutating that task unless ownership is explicitly transferred back.

## Resume from a handoff

1. Read applicable AGENTS instructions and the repository's navigation entry before the snapshot; treat those authorities as superior to the handoff.
2. Validate the snapshot's owning worktree, branch, PR, base, head, capture time, predecessor/successor state, and reproducible staged/unstaged/untracked fingerprint. Refresh live PR and CI state rather than trusting captured status.
3. Stop and report the mismatch if any invalidation condition applies, the worktree contains unknown changes, a newer snapshot exists, or another session still owns the task. Do not guess or silently repair the snapshot.
4. If validation succeeds, execute only the single `Next action` within the user's existing authorization. Create a successor snapshot for another transfer; never edit history in place.

## Safety boundaries

- Never stage, commit, push, merge, deploy, rebase, delete branches/worktrees/plans, or otherwise clean up merely because a handoff exists.
- Never claim that the snapshot proves CI success, Candidate verification, approval, or current implementation state.
- Keep durable facts in their owning docs, code, PR, issue, ADR, or test report. Keep the handoff small and disposable.
